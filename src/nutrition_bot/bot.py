import discord
from .config import DISCORD_BOT_TOKEN, JST
from .utils import get_exif_datetime
from .services import analyze_with_gemini, send_to_gas

# Discord Botの初期化
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.attachments and not message.content.strip():
        return

    image_bytes = None
    eaten_at_dt = None

    if message.attachments:
        attachment = message.attachments[0]
        if attachment.content_type and attachment.content_type.startswith("image/"):
            image_bytes = await attachment.read()
            eaten_at_dt = get_exif_datetime(image_bytes)

    if eaten_at_dt is None:
        eaten_at_dt = message.created_at.astimezone(JST)

    eaten_at_str = eaten_at_dt.isoformat()
    status_msg = await message.channel.send("🔄 AIで食事を解析中...")

    result_json = await analyze_with_gemini(image_bytes, message.content, eaten_at_str)

    if result_json and "meals" in result_json:
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

def run_bot():
    if not DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set.")
    else:
        client.run(DISCORD_BOT_TOKEN)
