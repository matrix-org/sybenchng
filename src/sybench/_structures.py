import attr
import treq


@attr.s
class Request:

    method = attr.ib()
    url = attr.ib()
    request_body = attr.ib()

    async def execute(self, url):

        resp = await treq.request(self.method, url + self.url, json=self.request_body)

        if resp.code != 200:
            raise Exception(await treq.content(resp))

        body = await treq.json_content(resp)
        return body


def generate_login(username, password):

    return Request("POST", "/_matrix/client/r0/login", {
        "type": "m.login.password",
        "user": username,
        "password": password
    })


def generate_room_join(token, room_id):

    return Request("POST", f"/_matrix/client/r0/rooms/{room_id}/join?access_token={token}", {})

def generate_room_create(token, name):

    return Request("POST", f"/_matrix/client/r0/createRoom?access_token={token}",
                   {
                       "preset": "public_chat",
                       "room_alias_name": name,
                       "creation_content": {
                           "m.federate": False
                       }
                   })

def generate_message(token, room_id, txn_id, body):

    return Request("PUT", f"/_matrix/client/r0/rooms/{room_id}/send/m.room.message/{txn_id}?access_token={token}",
                   {
                       "msgtype": "m.text",
                       "body": body
                   })
