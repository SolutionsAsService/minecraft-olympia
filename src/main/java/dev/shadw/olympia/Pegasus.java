package dev.shadw.olympia;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The winged horse. It is a horse underneath (tamed by riding it again and again, saddled with a saddle, healed with food) that, once saddled and
 * ridden, flies: hold jump to climb, look down while moving forward to dive, let go to hover, and it takes no fall damage. Its model, with beating
 * wings, is generated from mobs/pegasus.json; this class is hand-written because it is a mount.
 */
public class Pegasus extends AbstractHorse {
	/** Whether the jump key is down; set every client tick by OlympiaClient and read only on the client. */
	public static volatile boolean clientJumpHeld;

	public Pegasus(EntityType<? extends Pegasus> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return AbstractHorse.createBaseHorseAttributes()
				.add(Attributes.MAX_HEALTH, 30.0)
				.add(Attributes.MOVEMENT_SPEED, 0.3)
				.add(Attributes.JUMP_STRENGTH, 0.9);
	}

	@Override
	public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob other) {
		return null;
	}

	@Override
	public boolean canFallInLove() {
		return false;
	}

	@Override
	public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
		return false;
	}

	private boolean flying() {
		return isSaddled() && getControllingPassenger() instanceof Player;
	}

	/** A saddled, ridden pegasus does not fall: the rider steers its height. */
	@Override
	public boolean isNoGravity() {
		return super.isNoGravity() || flying();
	}

	/** In the air a ridden horse moves at a hundredth of its ground speed; a pegasus keeps a quarter of it. */
	@Override
	protected float getFlyingSpeed() {
		return flying() ? getSpeed() * 0.3F : super.getFlyingSpeed();
	}

	@Override
	protected void tickRidden(Player player, Vec3 input) {
		super.tickRidden(player, input);
		if (!flying()) {
			return;
		}
		boolean jump = level().isClientSide ? clientJumpHeld : player instanceof ServerPlayer sp && sp.getLastClientInput().jump();
		Vec3 motion = getDeltaMovement();
		double vy = motion.y * 0.8;
		if (jump) {
			vy = 0.32;
		} else if (input.z > 0.0 && !onGround()) {
			vy = -Math.sin(Math.toRadians(player.getXRot())) * 0.4;
		}
		setDeltaMovement(motion.x, Mth.clamp(vy, -0.5, 0.5), motion.z);
	}
}
