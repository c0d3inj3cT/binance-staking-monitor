# binance-staking-monitor
A Telegram bot to monitor Binance staking pools' status changes.

Binance offers different staking pools for different crypto currency assets. Each staking pool has a different duration and a different interest rate.

Usually staking pools for longer duration offer better interest rates. Due to the high demand, these staking pools open and close quickly.

The purpose of this bot is to allow you to receive an alert as soon as the status of the staking pool you are interested in changes.

Below are the main commands supported by the bot.

- /start - This command is used to print a summary of the bot.
- /set - This command is used to set an alert for a specific crypto currency asset.

Example:

/set DOT

The above command will set an alert for your userid and notify you as soon as the status of the staking pool of DOT changes on Binance.

- /clear - This command can be used to clear an alert which was set previously for a crypto currency asset.
