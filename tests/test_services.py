import pytest
from aioresponses import aioresponses
from nutrition_bot.services import send_to_gas
from nutrition_bot.config import GAS_WEBHOOK_URL

@pytest.mark.asyncio
async def test_send_to_gas_success():
    data = {"test": "data"}
    url = GAS_WEBHOOK_URL
    
    with aioresponses() as m:
        m.post(url, status=200)
        
        result = await send_to_gas(data)
        assert result is True

@pytest.mark.asyncio
async def test_send_to_gas_failure():
    data = {"test": "data"}
    url = GAS_WEBHOOK_URL
    
    with aioresponses() as m:
        m.post(url, status=400, body="Bad Request")
        
        result = await send_to_gas(data)
        assert result is False

@pytest.mark.asyncio
async def test_send_to_gas_exception():
    data = {"test": "data"}
    url = GAS_WEBHOOK_URL
    
    with aioresponses() as m:
        # ネットワーク例外をシミュレート
        m.post(url, exception=Exception("Connection error"))
        
        result = await send_to_gas(data)
        assert result is False
