import json, sys, uuid
import boto3

# Use your profile/region from `aws configure`
s3 = boto3.client("s3")
translate = boto3.client("translate")

# Set these to your stack outputs (Phase 2)
REQUEST_BUCKET  = "080577529709-request-bucket"   # e.g., 123456789012-request-bucket
RESPONSE_BUCKET = "080577529709-response-bucket"  # e.g., 123456789012-response-bucket

def main(input_path: str):
    # read local JSON
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    src = data.get("source_language", "auto")
    tgt = data["target_language"]
    text = data["text"]

    # call Translate
    resp = translate.translate_text(Text=text, SourceLanguageCode=src, TargetLanguageCode=tgt)
    out = {
        "original_text": text,
        "translated_text": resp["TranslatedText"],
        "source_language": src,
        "target_language": tgt
    }

    # write output to response bucket (unique key)
    key = f"translated/{uuid.uuid4()}.json"
    s3.put_object(Bucket=RESPONSE_BUCKET, Key=key, Body=json.dumps(out).encode("utf-8"))
    print(f"✅ Wrote s3://{RESPONSE_BUCKET}/{key}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python translate_local.py path/to/sample.json")
        sys.exit(1)
    main(sys.argv[1])
