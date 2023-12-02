from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

from models import Price, Url
from config import SYNC_DATABASE_URL


if __name__ == '__main__':
    engine = create_engine(url=SYNC_DATABASE_URL)
    sync_session = sessionmaker(engine)

    def up_db():
        with sync_session() as session:
            stmt = insert(Url).values(
                [{'title': 'main_image',
                  'url': "https://downloader.disk.yandex.ru/disk/08d579cad37c58eded4e83a85ab2"
                         "af90c5b2bb0d8f07f05ede2df63e3b7a2e9e/6501e0f8/mwTcy9e65zcqpq-YxMe9vP9"
                         "tXZKgtFrAaCtIyQDbxjFfHgcPIxHCj_mTAQdlVj70glWSIiXpCfT9NiSR7Vj6jQ%3D%3D?"
                         "uid=1444200119&filename=main.png&disposition=attachment&hash=&limit=0&c"
                         "ontent_type=image%2Fjpeg&owner_uid=1444200119&fsize=31195&hid=a3694ec940"
                         "692ebbaea9cf4f713b63a7&media_type=image&tknv=v2&etag=b69910347ccd18e39e3"
                         "2b2c5a8d40a4b"}
                 ]
            )
            session.execute(stmt)

            stmt = insert(Price).values(
                [{'product': 'Шаверма', 'price': 190, 'description': '...',
                 'url': 'https://downloader.disk.yandex.ru/disk/eacc1408f1a3c9fc628e7bf9c27467'
                        '1897d27f49676ee285111a94d90fbb627d/6501d243/mwTcy9e65zcqpq-YxMe9vB_X45'
                        '5bo6r3chVyuKF13olSTMiLxXD_YISEUQL4VqoBsmjg_uvQsGLZmZC4NklYeg%3D%3D?uid'
                        '=1444200119&filename=%D0%A8%D0%B0%D0%B2%D0%B5%D1%80%D0%BC%D0%B0.png&di'
                        'sposition=attachment&hash=&limit=0&content_type=image%2Fjpeg&owner_uid='
                        '1444200119&fsize=127927&hid=e06bdd3fefd46dcb92cac0d8b7a5acdd&media_type='
                        'image&tknv=v2&etag=8f0c0850d9d58ba534bd927775906e26'},

                 {'product': 'Шаурма', 'price': 190, 'description': '...',
                  'url': 'https://downloader.disk.yandex.ru/disk/28e8787fba8484b1be3d88d2aa99d6c'
                         '2da035a9915d4e494ae8e6c40821dfabb/6501de74/cYHidmqQOvt9VGJ4n8GG_dBy3ND'
                         'UfbP62xQHmdNTKNGwmB5OIRSbtl-xEArMSxpF1Zo5aGccEN2xWxogXYGuXg%3D%3D?uid='
                         '1444200119&filename=%D0%A8%D0%B0%D1%83%D1%80%D0%BC%D0%B0.png&dispositi'
                         'on=attachment&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=14442'
                         '00119&fsize=203442&hid=c6a090e2215ef505f8d170df91198848&media_type=ima'
                         'ge&tknv=v2&etag=deddfd8e68da23b7d3f227d27d15e2e2'},

                 {'product': 'Шаурма двойная', 'price': 240, 'description': '...',
                  'url': 'https://downloader.disk.yandex.ru/disk/d9e8f8ab28b849825fd589a55d5697'
                         '003c11a275a85767159beb7b9d1ed8e8e1/6501f068/mwTcy9e65zcqpq-YxMe9vOSkbl'
                         'I6JmUcu3E_y4dqttEQkjDRAK6M6bFITa3CpJDVFbDLwaZk0KN-VNhGaV2BfA%3D%3D?uid'
                         '=1444200119&filename=%D0%A8%D0%B0%D1%83%D1%80%D0%BC%D0%B0%20%D0%B4%D0%'
                         'B2%D0%BE%D0%B9%D0%BD%D0%B0%D1%8F.png&disposition=attachment&hash=&limi'
                         't=0&content_type=image%2Fjpeg&owner_uid=1444200119&fsize=255959&hid=16'
                         'a0dccf47b627d60002eaf32f706469&media_type=image&tknv=v2&etag=353bf09be'
                         '95aaff9def49b328933ce3e'},

                 {'product': 'Бургер', 'price': 250, 'description': '...',
                  'url': 'https://downloader.disk.yandex.ru/disk/fac2bb85f77f95805287d58096679f'
                         '57636ea7255e083c80eec6074155aad395/6501d78a/mwTcy9e65zcqpq-YxMe9vPFYc6'
                         '19ghSz36tHeOG6FSYKUa1POCLAB3eXAC0i8utVMnG39wCb2PI0pfi0P3HXVQ%3D%3D?uid'
                         '=1444200119&filename=%D0%91%D1%83%D1%80%D0%B3%D0%B5%D1%80.png&disposit'
                         'ion=attachment&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=14442'
                         '00119&fsize=140965&hid=e732a1dccc329fde6f0ca763a4e3e9ef&media_type=ima'
                         'ge&tknv=v2&etag=536c8500a7dfa3abb41b080eff361ca1'},

                 {'product': 'Картошка фри', 'price': 80, 'description': '...',
                  'url': 'https://downloader.disk.yandex.ru/disk/dae61e05a37dc1b5388d935e22085f5'
                         '6bc60c6357d4db305a9fe31e6e2705924/6501d45c/mwTcy9e65zcqpq-YxMe9vLjQCwt'
                         '-UbkknBogrmQsu7THq-Yp6wSQBYQEnl6wjmEnrP22GASLMHz2-bi-BoEjtw%3D%3D?uid=1'
                         '444200119&filename=%D0%9A%D0%B0%D1%80%D1%82%D0%BE%D1%88%D0%BA%D0%B0%20%'
                         'D1%84%D1%80%D0%B8.png&disposition=attachment&hash=&limit=0&content_type'
                         '=image%2Fjpeg&owner_uid=1444200119&fsize=179434&hid=4b60719e8ab270239f5'
                         '6f6588e3359cc&media_type=image&tknv=v2&etag=0f3ae412ac433ab2962f44089b2'
                         '03a65'},

                 {'product': 'Курица в панировке', 'price': 140, 'description': '...',
                  'url': 'https://downloader.disk.yandex.ru/disk/5ede046f4458d9eb45475fc654a131'
                         'b28ca9fb98d5ea0f088487d7d3d1ee29f7/6501ec9f/mwTcy9e65zcqpq-YxMe9vG-Nl'
                         'KjcoIJ8gf2cvlwZam0imknO_COSGBoqbr8NGS1a1e_SS8R7IxvNFprCyQtjVg%3D%3D?ui'
                         'd=1444200119&filename=%D0%9A%D1%83%D1%80%D0%B8%D1%86%D0%B0%20%D0%B2%2'
                         '0%D0%BF%D0%B0%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B5.png&dispositi'
                         'on=attachment&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=14442'
                         '00119&fsize=92135&hid=fbe8ba4b54a56c5824e220df515de5b4&media_type=imag'
                         'e&tknv=v2&etag=cc77369789d0a88bbbf3924c84bd6e08'}
                 ]
            )

            session.execute(stmt)
            session.commit()

    up_db()

