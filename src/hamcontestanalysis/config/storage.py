"""Storage settings for PyContestAnalyzer."""

from hamcontestanalysis.config.settings import BaseSettings


class StoragePathsSettings(BaseSettings):
    """S3 Paths Settings model."""

    raw_data: str
    raw_metadata: str
    raw_rbn: str
    temporary: str


class StorageSettings(BaseSettings):
    """Storage Settings model."""

    partitions: str
    prefix: str
    partitions_rbn: str

    @property
    def paths(self):
        """Render PyContestAnalyzer paths from settings.

        This method renders the paths for types in 'optimisation', 'performance' and
        'temporary' by interpolating:
        s3://{self.bucket}/{self.prefix}/{type}(/{self.partition})
        We do this instead of using Dynaconf Jinja2 templating to allow for overrides in
        the prefix via environment variables. This use case is needed on the staged
        executions to redirect S3 output on either environment.
        """
        return StoragePathsSettings(
            raw_data=(f"{self.prefix}/{self.partitions}/raw_data"),
            raw_metadata=(f"{self.prefix}/{self.partitions}/raw_metadata"),
            raw_rbn=(f"{self.prefix}/{self.partitions_rbn}/rbn"),
            temporary=f"{self.prefix}/temporary",
        )

    # pylint: disable=too-few-public-methods
    class Config:
        """Pydantic model config."""

        env_prefix = "PYCA_STORAGE__"
