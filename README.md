# SFERA AI — FaceFusion Docker RUN

Подготовка для Cloud.ru ML Inference → Docker RUN.

## Поля Cloud.ru
- Порт контейнера: `8080`
- Health probe: HTTP GET `/health`
- Переменная: `SFERA_API_TOKEN` = длинный случайный секрет
- `FACE_SWAPPER_MODEL=inswapper_128_fp16` (опционально)
- `JOB_TIMEOUT=900` (опционально)

## API
`GET /health`

`POST /swap` multipart/form-data:
- `face`: фото лица
- `video`: MP4
- Header: `Authorization: Bearer <SFERA_API_TOKEN>`

Возвращает MP4.

## Важно
Этот пакет — исходник Docker-образа. Сначала его надо собрать и отправить в Container Registry. После этого URI готового образа вставляется в Docker RUN.

Перед production обязательно проверить CLI выбранной версии FaceFusion и провести тест на одном ролике. Не использовать изображения/видео людей без необходимых прав или согласия.
