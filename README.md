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

## Изменения v2
- ONNX Runtime GPU 1.22.0 вместо CPU-пакета.
- /health отвечает во время обработки; один GPU-заказ одновременно, остальные получают 429.
- Таймаут обработки возвращает 504; временные файлы удаляются.
- Видео кодируется libx264 на CPU; замена лица использует CUDA. NVENC не требуется.

## GitHub Actions
Сохранить .github/workflows/docker.yml по указанному пути. В Actions выбрать Build FaceFusion → Run workflow. Первый запуск — publish выключен: только сборка и проверка API.
Для отправки в Cloud.ru нужны repository secrets CLOUDRU_REGISTRY_USER и CLOUDRU_REGISTRY_PASSWORD с данными входа в реестр. Их значения вводить только в GitHub Secrets. Затем запустить workflow с publish включённым.
Образ: sfera-facefusion.cr.cloud.ru/sfera-facefusion:latest (также тег SHA коммита).
Проверка на GitHub без GPU не подтверждает выполнение CUDA-инференса. Перед подключением к пользователям требуется тест /swap на GPU-сервере Cloud.ru с реальными файлами. Проверить лимит размера запроса и таймаут платформы для синхронного /swap.
