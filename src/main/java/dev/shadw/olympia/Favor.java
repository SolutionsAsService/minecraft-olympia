package dev.shadw.olympia;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.serialization.Codec;
import java.util.HashMap;
import java.util.Map;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.ItemStack;

/** Divine favor: offerings at a god's altar raise a per-player favor score, and favor stages decide which blessings come. */
public final class Favor {
	/** god id -> favor points, saved with the player and kept through death. */
	public static final AttachmentType<Map<String, Integer>> FAVOR = AttachmentRegistry.create(
			ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, "favor"),
			b -> b.persistent(Codec.unboundedMap(Codec.STRING, Codec.INT)).copyOnDeath().initializer(HashMap::new));

	private Favor() {}

	public static void init() {}

	public static int get(ServerPlayer player, String god) {
		return player.getAttachedOrCreate(FAVOR).getOrDefault(god, 0);
	}

	/** 0 Stranger, 1 Recognized, 2 Favored, 3 Chosen, by the thresholds in content.json. */
	public static int stage(int favor) {
		JsonArray stages = ContentData.root().getAsJsonObject("favor").getAsJsonArray("stages");
		int stage = 0;
		for (int i = 0; i < stages.size(); i++) {
			if (favor >= stages.get(i).getAsJsonObject().get("at").getAsInt()) {
				stage = i;
			}
		}
		return stage;
	}

	public static String stageName(int stage) {
		return ContentData.root().getAsJsonObject("favor").getAsJsonArray("stages").get(stage).getAsJsonObject().get("name").getAsString();
	}

	public static JsonObject god(String id) {
		return ContentData.root().getAsJsonObject("gods").getAsJsonObject(id);
	}

	/** How much favor this item is worth to the god, or 0 if the god does not want it. */
	public static int worth(String godId, ItemStack stack) {
		String key = BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
		for (JsonElement e : god(godId).getAsJsonArray("offerings")) {
			JsonObject o = e.getAsJsonObject();
			if (o.get("item").getAsString().equals(key)) {
				return o.get("favor").getAsInt();
			}
		}
		return 0;
	}

	/** Make an offering of one item. Returns true if the god accepted it. */
	public static boolean offer(ServerPlayer player, String godId, ItemStack stack) {
		JsonObject god = god(godId);
		String name = god.get("name").getAsString();
		int worth = stack.isEmpty() ? 0 : worth(godId, stack);
		if (worth == 0) {
			player.displayClientMessage(Component.literal(name + " does not want that."), true);
			return false;
		}
		if (!player.getAbilities().instabuild) {
			stack.shrink(1);
		}
		Map<String, Integer> map = new HashMap<>(player.getAttachedOrCreate(FAVOR));
		int before = map.getOrDefault(godId, 0);
		int after = before + worth;
		map.put(godId, after);
		player.setAttached(FAVOR, map);
		int oldStage = stage(before);
		int newStage = stage(after);
		for (JsonElement b : god.getAsJsonArray("blessings")) {
			JsonObject blessing = b.getAsJsonObject();
			if (blessing.get("stage").getAsInt() <= newStage) {
				for (JsonElement fx : blessing.getAsJsonArray("effects")) {
					JsonArray row = fx.getAsJsonArray();
					BuiltInRegistries.MOB_EFFECT.getOptional(ResourceLocation.parse(row.get(0).getAsString()))
							.map(BuiltInRegistries.MOB_EFFECT::wrapAsHolder)
							.ifPresent(h -> player.addEffect(new MobEffectInstance(h, row.get(1).getAsInt() * 20, row.get(2).getAsInt())));
				}
			}
		}
		String line = name + " accepts your offering. Favor " + after + " (" + stageName(newStage) + ").";
		if (newStage > oldStage) {
			line = name + " names you " + stageName(newStage) + ". Favor " + after + ".";
		}
		player.displayClientMessage(Component.literal(line), true);
		if (player.level() instanceof ServerLevel level) {
			level.playSound(null, player.blockPosition(), newStage > oldStage ? SoundEvents.UI_TOAST_CHALLENGE_COMPLETE : SoundEvents.AMETHYST_BLOCK_CHIME,
					SoundSource.PLAYERS, 0.8F, 1.2F);
			level.sendParticles(ParticleTypes.HAPPY_VILLAGER, player.getX(), player.getY() + 1.0, player.getZ(), 10, 0.4, 0.5, 0.4, 0.02);
		}
		return true;
	}
}
