from pathlib import Path
from typing import Final

BACKUP_ROOT: Final[Path] = Path("private") / "var"
DOMAIN_TRANSLATION: Final[dict[str, Path]] = {
    "AppDomain": BACKUP_ROOT / "mobile" / "Containers" / "Data" / "Application",
    "AppDomainGroup": BACKUP_ROOT / "mobile" / "Containers" / "Shared" / "AppGroup",
    "AppDomainPlugin": BACKUP_ROOT / "mobile" / "Containers" / "Data" / "PluginKitPlugin",
    "SysContainerDomain": BACKUP_ROOT / "containers" / "Data" / "System",
    "SysSharedContainerDomain": BACKUP_ROOT / "containers" / "Shared" / "SystemGroup",
    "KeychainDomain": BACKUP_ROOT / "Keychains",
    "CameraRollDomain": BACKUP_ROOT / "mobile",
    "MobileDeviceDomain": BACKUP_ROOT / "MobileDevice",
    "WirelessDomain": BACKUP_ROOT / "wireless",
    "InstallDomain": BACKUP_ROOT / "installd",
    "KeyboardDomain": BACKUP_ROOT / "mobile",
    "HomeDomain": BACKUP_ROOT / "mobile",
    "SystemPreferencesDomain": BACKUP_ROOT / "preferences",
    "DatabaseDomain": BACKUP_ROOT / "db",
    "TonesDomain": BACKUP_ROOT / "mobile",
    "RootDomain": BACKUP_ROOT / "root",
    "BooksDomain": BACKUP_ROOT / "mobile" / "Media" / "Books",
    "ManagedPreferencesDomain": BACKUP_ROOT / "Managed Preferences",
    "HomeKitDomain": BACKUP_ROOT / "mobile",
    "MediaDomain": BACKUP_ROOT / "mobile",
    "HealthDomain": BACKUP_ROOT / "mobile" / "Library"
}
