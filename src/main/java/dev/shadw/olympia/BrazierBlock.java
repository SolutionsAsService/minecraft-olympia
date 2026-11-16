package dev.shadw.olympia;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/** A sacred brazier: bright, with a flame and smoke rising from its bowl. */
public class BrazierBlock extends Block {
	public BrazierBlock(Properties properties) {
		super(properties);
	}

	@Override
	public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
		double x = pos.getX() + 0.5 + (random.nextDouble() - 0.5) * 0.5;
		double z = pos.getZ() + 0.5 + (random.nextDouble() - 0.5) * 0.5;
		if (random.nextInt(2) == 0) {
			level.addParticle(ParticleTypes.FLAME, x, pos.getY() + 1.05, z, 0.0, 0.02, 0.0);
		}
		if (random.nextInt(5) == 0) {
			level.addParticle(ParticleTypes.SMOKE, x, pos.getY() + 1.1, z, 0.0, 0.04, 0.0);
		}
	}
}
