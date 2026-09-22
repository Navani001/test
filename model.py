import boto3

from typing import Iterator

from botocore.exceptions import ClientError


class S3Service:

    def __init__(
        self,
        bucket_name: str,
        prefix: str = "",
        region_name: str | None = None,
    ):
        self.bucket_name = bucket_name
        self.prefix = prefix

        self.client = boto3.client(
            "s3",
            region_name=region_name,
        )

    def list_logs(self) -> Iterator[dict]:
        """
        Get all objects from the configured S3 prefix.

        Returns:
            {
                "key": str,
                "etag": str,
                "size": int,
                "last_modified": datetime
            }
        """

        paginator = self.client.get_paginator(
            "list_objects_v2"
        )

        try:

            for page in paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=self.prefix,
            ):

                for obj in page.get(
                    "Contents",
                    []
                ):

                    key = obj["Key"]

                    # Ignore S3 folders
                    if key.endswith("/"):
                        continue

                    yield {
                        "key": key,
                        "etag": obj["ETag"].strip('"'),
                        "size": obj["Size"],
                        "last_modified": obj[
                            "LastModified"
                        ],
                    }

        except ClientError as exc:

            raise RuntimeError(
                f"Failed to list S3 logs: {exc}"
            ) from exc

    def download_log(
        self,
        key: str,
    ) -> str:

        try:

            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            body = response["Body"]

            try:

                return body.read().decode(
                    "utf-8",
                    errors="replace",
                )

            finally:

                body.close()

        except ClientError as exc:

            raise RuntimeError(
                f"Failed to download "
                f"S3 log '{key}': {exc}"
            ) from exc
            
