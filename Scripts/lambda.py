import json, os, logging, boto3

s3 = boto3.client("s3")
translate = boto3.client("translate")
log = logging.getLogger()
log.setLevel(logging.INFO)

def lambda_handler(event, context):
    for rec in event.get("Records", []):
        b = rec["s3"]["bucket"]["name"]
        k = rec["s3"]["object"]["key"]
        log.info(f"Processing s3://{b}/{k}")

        obj = s3.get_object(Bucket=b, Key=k)
        data = json.loads(obj["Body"].read().decode("utf-8"))

        # handle single object or batch
        items = data.get("items") if isinstance(data, dict) and "items" in data else [data]

        translated_items = []
        for it in items:
            src = it.get("source_language", "auto")
            tgt = it["target_language"]
            txt = it["text"]

            resp = translate.translate_text(
                Text=txt,
                SourceLanguageCode=src,
                TargetLanguageCode=tgt
            )

            # return same structure, just with translated_text
            translated_items.append({
                "source_language": src,
                "target_language": tgt,
                "original_text": txt,
                "translated_text": resp["TranslatedText"]
            })

        # output = single item if input was single, otherwise list
        out = translated_items[0] if len(translated_items) == 1 else translated_items

        # change filename: test.json -> test-output.json
        base, ext = k.rsplit('.', 1)
        out_key = f"{base}-output.{ext}"

        s3.put_object(
            Bucket=os.environ["OUTPUT_BUCKET"],
            Key=out_key,
            Body=json.dumps(out, ensure_ascii=False).encode("utf-8")
        )
        log.info(f"Wrote s3://{os.environ['OUTPUT_BUCKET']}/{out_key}")
