from locust import HttpUser, task, between
import time

class AnalyzeUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def analyze_audio(self):
        with open("/Users/muhammedamr/Desktop/AHBS/Medical_voice_assistant/uploads/dr_elshwtfy.ogg", "rb") as audio_file:
            files = {"audio": ("dr_elshwtfy.ogg", audio_file, "audio/ogg")}
            data = {"language": "ar"}

            start_time = time.time()
            got_first = False

            with self.client.post(
                "/analyze",
                files=files,
                data=data,
                stream=True,
                catch_response=True
            ) as response:
                try:
                    for line in response.iter_lines():
                        if not got_first and line:
                            # record time to first response
                            ttfr = (time.time() - start_time) * 1000
                            self.environment.events.request.fire(
                                request_type="POST",
                                name="/analyze_ttfr",
                                response_time=ttfr,
                                response_length=len(line),
                                response=response
                            )
                            got_first = True

                    # after stream ends, record total time
                    ttfs = (time.time() - start_time) * 1000
                    self.environment.events.request.fire(
                        request_type="POST",
                        name="/analyze_ttfs",
                        response_time=ttfs,
                        response_length=0,
                        response=response
                    )

                    response.success()

                except Exception as e:
                    response.failure(f"Stream error: {str(e)}")
