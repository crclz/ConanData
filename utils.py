import swagger_client as conan
import os


class Api:
    def __init__(self):
        self.conf = conan.Configuration()
        self.conf.host = "http://localhost:3923"
        self.client = conan.ApiClient(configuration=self.conf)
        self.access_api = conan.AccessApi(api_client=self.client)
        self.video_api = conan.VideosApi(api_client=self.client)
        self.storyline_api = conan.StoryLinesApi(api_client=self.client)

    def login(self, username, password):
        login_model = conan.LoginModel(username=username, password=password)
        token = self.access_api.login(body=login_model)
        self.client.default_headers['Conan-LoginInfo'] = token

        me = self.access_api.get_me()
        me: conan.QUser
        assert me.id is not None

    def login_as_admin(self):
        self.login('admin', os.environ['CONAN_ADMIN_PASS'])


if __name__ == '__main__':
    api = Api()
    api.login_as_admin()

    print("Test ok")

    os._exit(0)
