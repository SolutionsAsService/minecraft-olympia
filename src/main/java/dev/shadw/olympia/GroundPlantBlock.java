package dev.shadw.olympia;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.FlowerBlock;
import net.minecraft.world.level.block.state.BlockState;

/** A Mediterranean plant (laurel): it grows on grass, dirt, sand and gravel. */
public class GroundPlantBlock extends FlowerBlock {
	public GroundPlantBlock(Holder<MobEffect> effect, float seconds, Properties properties) {
		super(effect, seconds, properties);
	}

	@Override
	protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
		return state.is(BlockTags.DIRT) || state.is(BlockTags.SAND) || state.is(net.minecraft.world.level.block.Blocks.GRAVEL);
	}
}
