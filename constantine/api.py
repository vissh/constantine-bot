import datetime
import re
import sys
import time
from functools import partial
from threading import Lock

from telebot import TeleBot
from telebot.util import ThreadPool

from constantine.jenkins import JobRunner
from constantine.speech import reply_speech

WAIT_TIME = 9

pending_jobs = {}
pending_jobs_lock = Lock()


class Bot(TeleBot):
    def __init__(self, token, threaded=True, skip_pending=False):
        super().__init__(token, threaded, skip_pending)
        self.worker_pool = ThreadPool(num_threads=4)

    def process_new_messages(self, new_messages):
        result = []
        for new_message in new_messages:
            if new_message.date < time.time() - 180:
                continue
            result.append(new_message)

        if result:
            super().process_new_messages(result)


class Job:
    def __init__(self, bot_msg, build_tak):
        self.bot_msg = bot_msg
        self.bot_msg_id = bot_msg.message_id
        self.human_msg_id = bot_msg.reply_to_message.message_id
        self.chat_id = bot_msg.chat.id
        self.build_task = build_tak


class Constantine:
    build_pattern = re.compile('/build_(\w*)@?')

    def __init__(self, token, jenkins_url, jenkins_username, jenkins_password,
                 jobs_names):
        self.bot = Bot(token)
        self.jenkins_url = jenkins_url
        self.jenkins_username = jenkins_username
        self.jenkins_password = jenkins_password
        self.jobs_names = jobs_names

    def wake_up(self):
        JobRunner.jenkins_auth(self)
        self.subscription()
        sys.stdout.write('{} Bot running\n'.format(datetime.datetime.now()))
        self.bot.polling(none_stop=True)

    def subscription(self):
        self.bot.message_handler(regexp='/build_.*')(self.build_handler)
        self.bot.message_handler(regexp='/cancel_.*')(self.cancel_handler)
        self.bot.message_handler(func=lambda m: True)(self.all_handler)

    def exec_task(self, *args, **kwargs):
        return self.bot._exec_task(*args, **kwargs)

    def build_handler(self, msg):
        result = self.build_pattern.match(msg.text)
        if result and result.group(1) in self.jobs_names:
            self.build_job(msg, self.jobs_names[result.group(1)])

    def cancel_handler(self, message):
        str_cancel_msg_id = message.text[len('/cancel_'):]
        if not str_cancel_msg_id.isdigit():
            return

        cancel_msg_id = int(str_cancel_msg_id)
        with pending_jobs_lock:
            if cancel_msg_id in pending_jobs:
                job = pending_jobs[cancel_msg_id]
                del pending_jobs[cancel_msg_id]
                self.bot.edit_message_text('Отменено.',
                                           chat_id=job.chat_id,
                                           message_id=job.bot_msg_id)

    def all_handler(self, message):
        reply_speech(self, message)

    def build_job(self, msg, job_name):
        bot_msg = self.bot.reply_to(msg, wait_msg(WAIT_TIME, msg.message_id))
        job = Job(bot_msg, job_name)
        pending_jobs[job.human_msg_id] = job
        self.exec_task(self.countdown_task, job, time.time(), WAIT_TIME - 1)

    def countdown_task(self, job, start, wait_time):
        retry = partial(self.exec_task, self.countdown_task, job, start,
                        wait_time)

        if time.time() - start < 0.91:
            return retry()

        if not pending_jobs_lock.acquire(False):
            return retry()

        try:
            if not wait_time:
                if pending_jobs.pop(job.human_msg_id, False):
                    runner = JobRunner(self, job)
                    self.exec_task(runner.build)
            else:
                cancel = job.human_msg_id not in pending_jobs
                if not cancel:
                    text = wait_msg(wait_time, job.human_msg_id)
                    self.bot.edit_message_text(text, chat_id=job.chat_id,
                                               message_id=job.bot_msg_id)
                    self.exec_task(self.countdown_task, job, time.time(),
                                   wait_time - 1)
        finally:
            pending_jobs_lock.release()


def wait_msg(wait_time, msg_id):
    return 'Запущу через {0}. Отменить /cancel_{1}.'.format(wait_time, msg_id)
