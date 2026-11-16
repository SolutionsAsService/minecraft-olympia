package dev.shadw.olympia;

import java.util.ArrayDeque;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The bull-headed thing in the labyrinth. It hunts: it tracks the nearest player through walls out to its follow range, charges
 * when you are in the open, slams the ground when you are close, and enrages below half health. It never leaves; it has a boss bar.
 */
public class Minotaur extends Zombie {
	private static final ResourceLocation ENRAGE_ID = ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, "enrage");
	private final ServerBossEvent bossBar = new ServerBossEvent(Component.translatable("entity.olympia.minotaur"),
			BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.PROGRESS);
	private int chargeCooldown = 60;
	private int slamCooldown = 40;
	private boolean enraged;

	public Minotaur(EntityType<? extends Minotaur> type, Level level) {
		super(type, level);
		this.xpReward = 50;
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Zombie.createAttributes()
				.add(Attributes.MAX_HEALTH, ContentData.d("creatures.minotaur", "health"))
				.add(Attributes.ATTACK_DAMAGE, ContentData.d("creatures.minotaur", "damage"))
				.add(Attributes.ARMOR, ContentData.d("creatures.minotaur", "armor"))
				.add(Attributes.MOVEMENT_SPEED, ContentData.d("creatures.minotaur", "speed"))
				.add(Attributes.KNOCKBACK_RESISTANCE, ContentData.d("creatures.minotaur", "knockback_resistance"))
				.add(Attributes.FOLLOW_RANGE, ContentData.d("creatures.minotaur", "follow_range"))
				.add(Attributes.SCALE, ContentData.d("creatures.minotaur", "scale"))
				.add(Attributes.SPAWN_REINFORCEMENTS_CHANCE, 0.0);
	}

	@Override
	protected void registerGoals() {
		super.registerGoals();
		// hunt without needing to see the player (mustSee = false), re-checked every 10 ticks
		// (the mustSee flag only matters once a target is held; acquiring one checks line of sight unless the conditions say not to)
		this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false, null) {
			{
				this.targetConditions.ignoreLineOfSight();
			}
		});
		// and walk the maze toward the target when the stock pathfinder cannot find a way
		this.goalSelector.addGoal(1, new StalkGoal());
	}

	/** A breadth-first route over the floor tiles at this level, from the Minotaur to a tile next to the target; empty if none. */
	private List<BlockPos> route(LivingEntity target) {
		BlockPos start = blockPosition();
		BlockPos goal = target.blockPosition();
		int y = start.getY();
		Map<BlockPos, BlockPos> from = new HashMap<>();
		ArrayDeque<BlockPos> queue = new ArrayDeque<>();
		from.put(start, start);
		queue.add(start);
		BlockPos found = null;
		int visited = 0;
		int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
		while (!queue.isEmpty() && visited++ < 6000) {
			BlockPos cur = queue.poll();
			if (Math.abs(cur.getX() - goal.getX()) <= 1 && Math.abs(cur.getZ() - goal.getZ()) <= 1 && Math.abs(goal.getY() - y) <= 3) {
				found = cur;
				break;
			}
			for (int[] d : dirs) {
				BlockPos next = new BlockPos(cur.getX() + d[0], y, cur.getZ() + d[1]);
				if (from.containsKey(next) || Math.abs(next.getX() - start.getX()) > 100 || Math.abs(next.getZ() - start.getZ()) > 100 || !walkable(next)) {
					continue;
				}
				from.put(next, cur);
				queue.add(next);
			}
		}
		if (found == null) {
			return Collections.emptyList();
		}
		java.util.ArrayList<BlockPos> path = new java.util.ArrayList<>();
		for (BlockPos p = found; !p.equals(start); p = from.get(p)) {
			path.add(p);
		}
		Collections.reverse(path);
		return path;
	}

	/** A floor tile this size of creature can stand on: three clear blocks above, something solid below. */
	private boolean walkable(BlockPos pos) {
		Level lvl = level();
		for (int dy = 0; dy < 3; dy++) {
			BlockPos p = pos.above(dy);
			if (!lvl.getBlockState(p).getCollisionShape(lvl, p).isEmpty()) {
				return false;
			}
		}
		BlockPos below = pos.below();
		return !lvl.getBlockState(below).getCollisionShape(lvl, below).isEmpty();
	}

	/** Takes over from the melee goal when the stock path to the target is missing or does not reach it. */
	private class StalkGoal extends Goal {
		private int nextCheck;
		private int age;
		private boolean done;

		StalkGoal() {
			setFlags(EnumSet.of(Goal.Flag.MOVE));
		}

		@Override
		public boolean canUse() {
			LivingEntity target = getTarget();
			if (target == null || !target.isAlive() || tickCount < nextCheck || distanceToSqr(target) < 6.0) {
				return false;
			}
			nextCheck = tickCount + 10;
			Path stock = getNavigation().createPath(target, 0);
			return (stock == null || !stock.canReach()) && !route(target).isEmpty();
		}

		@Override
		public boolean canContinueToUse() {
			LivingEntity target = getTarget();
			return target != null && target.isAlive() && !done && distanceToSqr(target) >= 6.0;
		}

		@Override
		public void start() {
			age = 0;
			done = false;
			steer();
		}

		@Override
		public void tick() {
			age++;
			if (age % 5 == 0) {
				steer();
			}
			if (age % 20 == 0) {
				LivingEntity target = getTarget();
				Path stock = target == null ? null : getNavigation().createPath(target, 0);
				done = stock != null && stock.canReach();       // the stock pathfinder can take it from here
			}
		}

		@Override
		public void stop() {
			getNavigation().stop();
		}

		private void steer() {
			LivingEntity target = getTarget();
			if (target == null) {
				return;
			}
			List<BlockPos> path = route(target);
			if (path.isEmpty()) {
				done = true;                                    // no way through to the target from here
				return;
			}
			BlockPos wp = path.get(Math.min(3, path.size() - 1));
			getNavigation().moveTo(wp.getX() + 0.5, wp.getY(), wp.getZ() + 0.5, 1.1);
		}
	}

	@Override
	protected boolean isSunSensitive() {
		return false;
	}

	@Override
	protected boolean convertsInWater() {
		return false;
	}

	@Override
	public boolean isBaby() {
		return false;
	}

	@Override
	public boolean removeWhenFarAway(double distance) {
		return false;
	}

	@Override
	public void startSeenByPlayer(ServerPlayer player) {
		super.startSeenByPlayer(player);
		bossBar.addPlayer(player);
	}

	@Override
	public void stopSeenByPlayer(ServerPlayer player) {
		super.stopSeenByPlayer(player);
		bossBar.removePlayer(player);
	}

	@Override
	protected void customServerAiStep(ServerLevel level) {
		super.customServerAiStep(level);
		bossBar.setProgress(getHealth() / getMaxHealth());
		if (chargeCooldown > 0) {
			chargeCooldown--;
		}
		if (slamCooldown > 0) {
			slamCooldown--;
		}
		if (!enraged && getHealth() < getMaxHealth() * 0.5F) {
			enraged = true;
			getAttribute(Attributes.MOVEMENT_SPEED).addOrReplacePermanentModifier(new AttributeModifier(ENRAGE_ID, 0.25, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
			getAttribute(Attributes.ATTACK_DAMAGE).addOrReplacePermanentModifier(new AttributeModifier(ENRAGE_ID, 0.4, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
			level.playSound(null, blockPosition(), SoundEvents.RAVAGER_ROAR, SoundSource.HOSTILE, 3.0F, 0.6F);
			bossBar.setColor(BossEvent.BossBarColor.PURPLE);
		}
		LivingEntity target = getTarget();
		if (target == null) {
			return;
		}
		double dist = distanceTo(target);
		int minCharge = ContentData.i("creatures.minotaur", "charge_min");
		int maxCharge = ContentData.i("creatures.minotaur", "charge_max");
		if (chargeCooldown == 0 && dist >= minCharge && dist <= maxCharge && hasLineOfSight(target)) {
			addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, ContentData.i("creatures.minotaur", "charge_seconds") * 20, enraged ? 3 : 2));
			level.playSound(null, blockPosition(), SoundEvents.RAVAGER_ROAR, SoundSource.HOSTILE, 2.0F, 0.9F);
			chargeCooldown = ContentData.i("creatures.minotaur", "charge_cooldown_ticks") / (enraged ? 2 : 1);
		}
		double radius = ContentData.d("creatures.minotaur", "slam_radius");
		if (slamCooldown == 0 && dist <= radius) {
			slam(level, radius);
			slamCooldown = ContentData.i("creatures.minotaur", "slam_cooldown_ticks") / (enraged ? 2 : 1);
		}
	}

	private void slam(ServerLevel level, double radius) {
		level.playSound(null, blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 1.5F, 0.7F);
		level.sendParticles(ParticleTypes.EXPLOSION, getX(), getY() + 0.2, getZ(), 6, radius / 3, 0.1, radius / 3, 0.0);
		List<LivingEntity> hit = level.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(radius, 1.0, radius), e -> e != this);
		for (LivingEntity e : hit) {
			e.hurtServer(level, damageSources().mobAttack(this), (float) ContentData.d("creatures.minotaur", "slam_damage"));
			Vec3 away = e.position().subtract(position()).multiply(1, 0, 1).normalize().scale(1.1);
			e.push(away.x, 0.6, away.z);
			e.hurtMarked = true;
		}
	}
}
