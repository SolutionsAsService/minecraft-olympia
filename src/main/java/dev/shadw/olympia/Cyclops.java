package dev.shadw.olympia;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** A one-eyed brute of the hills: large, slow to move, hard to push, and its blows throw you. */
public class Cyclops extends Zombie {
	public Cyclops(EntityType<? extends Cyclops> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Zombie.createAttributes()
				.add(Attributes.MAX_HEALTH, ContentData.d("creatures.cyclops", "health"))
				.add(Attributes.ATTACK_DAMAGE, ContentData.d("creatures.cyclops", "damage"))
				.add(Attributes.ARMOR, ContentData.d("creatures.cyclops", "armor"))
				.add(Attributes.MOVEMENT_SPEED, ContentData.d("creatures.cyclops", "speed"))
				.add(Attributes.KNOCKBACK_RESISTANCE, ContentData.d("creatures.cyclops", "knockback_resistance"))
				.add(Attributes.SCALE, ContentData.d("creatures.cyclops", "scale"))
				.add(Attributes.SPAWN_REINFORCEMENTS_CHANCE, 0.0);
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
	public boolean doHurtTarget(ServerLevel level, Entity target) {
		boolean hit = super.doHurtTarget(level, target);
		if (hit && target instanceof LivingEntity living) {
			Vec3 push = living.position().subtract(position()).multiply(1, 0, 1).normalize().scale(1.2);
			living.push(push.x, 0.45, push.z);
			living.hurtMarked = true;
		}
		return hit;
	}
}
