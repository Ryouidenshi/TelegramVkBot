class ProgressBar:
    def __init__(self, percent, bot, progressMessage):
        self.bot = bot
        self.percent = percent
        self.progressMessage = progressMessage

    def update_progress_bar(self, percent, text):
        countBar = (percent // 10)
        strBarPercent = '[' + '|' * int(countBar) + ' ' * ((10 - int(countBar)) * 2) + '] - ' + str(percent) + '%'
        self.bot.edit_message_text(text + '\n' + strBarPercent,
                                   self.progressMessage.chat.id, self.progressMessage.message_id)

    def __del__(self):
        print('DeletedProgressbar')
