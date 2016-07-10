import time

from jenkinsapi.jenkins import Jenkins


class JobRunner:
    def __init__(self, constantine, job):
        self.constantine = constantine
        self.job = job

    @classmethod
    def jenkins_auth(cls, constantine):
        return Jenkins(constantine.jenkins_url, constantine.jenkins_username,
                       constantine.jenkins_password)

    def build(self):
        self.constantine.bot.edit_message_text(
            'Запускаю.', chat_id=self.job.chat_id,
            message_id=self.job.bot_msg_id)
        self.constantine.exec_task(self.auth)

    def auth(self):
        jenkins = self.jenkins_auth(self.constantine)
        self.constantine.exec_task(self.build_job_step1, jenkins)

    def build_job_step1(self, jenkins):
        build = jenkins[self.job.build_task].get_last_build_or_none()
        self.constantine.exec_task(self.build_job_step2, jenkins, build)

    def build_job_step2(self, jenkins, build):
        if build:
            if not build.is_running():
                build = None

        self.constantine.exec_task(self.build_job_step3, jenkins, build)

    def build_job_step3(self, jenkins, build):
        if build:
            self.constantine.bot.edit_message_text(
                'В процессе.', chat_id=self.job.chat_id,
                message_id=self.job.bot_msg_id)
        else:
            queue = jenkins[self.job.build_task].invoke(build_params={})
            build = queue.block_until_building(delay=1)
            self.constantine.bot.edit_message_text(
                'Запустил.', chat_id=self.job.chat_id,
                message_id=self.job.bot_msg_id)

        self.constantine.exec_task(
            self.track_build, jenkins, build.buildno, time.time())

    def track_build(self, jenkins, build_number, start_time):
        if time.time() - start_time < 7:
            return self.constantine.exec_task(
                self.track_build, jenkins, build_number, start_time)

        jenkins_job = jenkins[self.job.build_task]

        if not jenkins_job.get_build(build_number).is_running():

            if jenkins_job.get_build(build_number).is_good():
                self.constantine.bot.reply_to(
                    self.job.bot_msg.reply_to_message,
                    'Обновление успешно завершилось.')
            else:
                self.constantine.bot.reply_to(
                    self.job.bot_msg.reply_to_message,
                    'Обновление провалилось.')
        else:
            self.constantine.exec_task(
                self.track_build, jenkins, build_number, time.time())
