import discord
from discord import app_commands
from discord.ext import commands
from .config import DISCORD_BOT_TOKEN, JST
from .utils import get_exif_datetime
from .services import analyze_with_gemini, send_to_gas


class NutritionBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        # プレフィックスコマンドは使用しないが、Botクラスを継承するために必要
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # スラッシュコマンドをグローバルに同期
        await self.tree.sync()
        print("Synced slash commands.")

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def process_meal_data(self, target, image_bytes, content, eaten_at_dt):
        """
        共通の食事解析・保存ロジック
        target: discord.abc.Messageable (チャンネル) または discord.Interaction
        """
        eaten_at_str = eaten_at_dt.isoformat()

        # 応答用のメッセージを準備
        if isinstance(target, discord.Interaction):
            if not target.response.is_done():
                await target.response.send_message("🔄 AIで食事を解析中...")
            status_msg = await target.original_response()
        else:
            status_msg = await target.send("🔄 AIで食事を解析中...")

        # Geminiで解析
        result_json = await analyze_with_gemini(image_bytes, content, eaten_at_str)

        if result_json and "meals" in result_json:
            # GAS (Google Apps Script) に送信
            success = await send_to_gas(result_json)

            if success:
                meals = result_json["meals"]
                formatted_reply = f"✅ **記録完了** ({len(meals)}品目)\n\n"

                for meal in meals:
                    formatted_reply += (
                        f"🍽 **{meal.get('menu')}**\n"
                        f"  🔥 {meal.get('calories')} kcal  |  💪 P: {meal.get('protein')}g  |  🥑 F: {meal.get('fat')}g  |  🍚 C: {meal.get('carb')}g\n"
                    )
                    if meal.get("source_url"):
                        formatted_reply += f"  🔗 [参考元]({meal.get('source_url')})\n"
                    formatted_reply += "\n"

                await status_msg.edit(content=formatted_reply.strip())
            else:
                await status_msg.edit(
                    content="❌ 解析は成功しましたが、スプレッドシートへの保存に失敗しました。"
                )
        else:
            await status_msg.edit(
                content="❌ AI解析に失敗しました。画像やテキストが食事と認識できなかった可能性があります。"
            )


bot = NutritionBot()


async def is_owner(interaction: discord.Interaction) -> bool:
    return await bot.is_owner(interaction.user)


@bot.tree.command(name="record", description="食事を記録します（DM限定・オーナー専用）")
@app_commands.describe(image="食事の画像", memo="食事の内容（テキスト）")
@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=False, dms=True, private_channels=False)
@app_commands.check(is_owner)
async def record(
    interaction: discord.Interaction,
    image: discord.Attachment | None = None,
    memo: str | None = None,
):
    # 入力チェック
    if not image and (not memo or not memo.strip()):
        await interaction.response.send_message(
            "画像またはテキストのどちらかを入力してください。", ephemeral=True
        )
        return

    image_bytes = None
    eaten_at_dt = None

    if image:
        if image.content_type and image.content_type.startswith("image/"):
            image_bytes = await image.read()
            eaten_at_dt = get_exif_datetime(image_bytes)
        else:
            await interaction.response.send_message(
                "画像ファイルを指定してください。", ephemeral=True
            )
            return

    if eaten_at_dt is None:
        eaten_at_dt = interaction.created_at.astimezone(JST)

    await bot.process_meal_data(interaction, image_bytes, memo or "", eaten_at_dt)


def run_bot():
    if not DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set.")
    else:
        bot.run(DISCORD_BOT_TOKEN)
