package dev.shadw.olympia;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.blockrenderlayer.v1.BlockRenderLayerMap;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ZombieRenderer;
import net.minecraft.client.renderer.entity.state.ZombieRenderState;
import net.minecraft.resources.ResourceLocation;

/** Client side: the creatures reuse the zombie model with their own skins; leaves and laurel are cut out. */
public class OlympiaClient implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		// textures with transparent pixels: without a cutout layer they render with a black background
		BlockRenderLayerMap.INSTANCE.putBlocks(RenderType.cutout(), OlympiaBlocks.LAUREL, OlympiaBlocks.OLIVE_LEAVES);
		dev.shadw.olympia.mobs.GeneratedMobsClient.initClient();
	}
}
