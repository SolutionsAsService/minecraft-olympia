package dev.shadw.olympia;

import com.google.gson.JsonObject;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/** /olympia favor shows your standing with each god. The operator commands offer the held item (the same code as the altar) and set a god's favor, for testing. */
public final class OlympiaCommands {
	private OlympiaCommands() {}

	public static void init() {
		CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> dispatcher.register(
				Commands.literal("olympia")
						.then(Commands.literal("favor").executes(ctx -> favor(ctx.getSource())))
						.then(Commands.literal("offer").requires(src -> src.hasPermission(2))
								.then(Commands.argument("god", StringArgumentType.word())
										.executes(ctx -> offer(ctx.getSource(), StringArgumentType.getString(ctx, "god")))))
						.then(Commands.literal("use").requires(src -> src.hasPermission(2)).executes(ctx -> use(ctx.getSource())))
						.then(Commands.literal("thread").requires(src -> src.hasPermission(2)).executes(ctx -> thread(ctx.getSource())))
						.then(Commands.literal("setfavor").requires(src -> src.hasPermission(2))
								.then(Commands.argument("god", StringArgumentType.word())
										.then(Commands.argument("points", com.mojang.brigadier.arguments.IntegerArgumentType.integer(0, 1000))
												.executes(ctx -> setFavor(ctx.getSource(), StringArgumentType.getString(ctx, "god"),
														com.mojang.brigadier.arguments.IntegerArgumentType.getInteger(ctx, "points"))))))));
	}

	private static int favor(CommandSourceStack source) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer player = source.getPlayerOrException();
		for (String id : OlympiaBlocks.GODS) {
			JsonObject god = Favor.god(id);
			int favor = Favor.get(player, id);
			source.sendSuccess(() -> Component.literal(god.get("name").getAsString() + ": favor " + favor + " ("
					+ Favor.stageName(Favor.stage(favor)) + ")"), false);
		}
		return 1;
	}

	private static int offer(CommandSourceStack source, String god) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		if (!java.util.Arrays.asList(OlympiaBlocks.GODS).contains(god)) {
			source.sendFailure(Component.literal("Unknown god '" + god + "'. Known: " + String.join(", ", OlympiaBlocks.GODS)));
			return 0;
		}
		ServerPlayer player = source.getPlayerOrException();
		boolean accepted = Favor.offer(player, god, player.getMainHandItem());
		int favor = Favor.get(player, god);
		source.sendSuccess(() -> Component.literal((accepted ? "Accepted. " : "Refused. ") + Favor.god(god).get("name").getAsString()
				+ " favor " + favor + " (" + Favor.stageName(Favor.stage(favor)) + ")"), false);
		return accepted ? 1 : 0;
	}

	private static int setFavor(CommandSourceStack source, String god, int points) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		if (!java.util.Arrays.asList(OlympiaBlocks.GODS).contains(god)) {
			source.sendFailure(Component.literal("Unknown god '" + god + "'. Known: " + String.join(", ", OlympiaBlocks.GODS)));
			return 0;
		}
		ServerPlayer player = source.getPlayerOrException();
		java.util.Map<String, Integer> map = new java.util.HashMap<>(player.getAttachedOrCreate(Favor.FAVOR));
		map.put(god, points);
		player.setAttached(Favor.FAVOR, map);
		source.sendSuccess(() -> Component.literal(Favor.god(god).get("name").getAsString() + " favor set to " + points + " ("
				+ Favor.stageName(Favor.stage(points)) + ")"), false);
		return 1;
	}

	/** Runs the held item's use() exactly as a right click does, so relics can be tested over RCON. */
	private static int use(CommandSourceStack source) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer player = source.getPlayerOrException();
		net.minecraft.world.item.ItemStack stack = player.getMainHandItem();
		var result = stack.getItem().use(player.level(), player, net.minecraft.world.InteractionHand.MAIN_HAND);
		source.sendSuccess(() -> Component.literal("use(" + net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(stack.getItem()) + ") -> " + result), false);
		return 1;
	}

	/** What the held Thread of Ariadne would say, as chat text (the item itself says it on the action bar). */
	private static int thread(CommandSourceStack source) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer player = source.getPlayerOrException();
		net.minecraft.world.phys.Vec3 knot = ThreadItem.knot(player.getMainHandItem(), player.level());
		source.sendSuccess(() -> Component.literal(knot == null ? "The thread is not tied." : ThreadItem.describe(knot.subtract(player.position()))), false);
		return knot == null ? 0 : 1;
	}
}
