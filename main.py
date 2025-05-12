from ErisPulse import sdk, logger
import asyncio

async def main():
    sdk.init()
    
    if hasattr(sdk, "YunhuAdapter"):
        if hasattr(sdk, "YunhuNormalHandler"):
            sdk.YunhuAdapter.AddTrigger(sdk.YunhuNormalHandler)
        if hasattr(sdk, "YunhuCommandHandler"):
            sdk.YunhuAdapter.AddTrigger(sdk.YunhuCommandHandler)
        if hasattr(sdk, "YunhuBotFollowed"):
            sdk.YunhuAdapter.AddTrigger(sdk.YunhuBotFollowed)

        if hasattr(sdk, "RemindCore"):
            await sdk.RemindCore.start()
            
        try:
            await sdk.YunhuAdapter.Run()
        finally:
            if hasattr(sdk, "RemindCore"):
                await sdk.RemindCore.stop()

if __name__ == "__main__":
    asyncio.run(main())