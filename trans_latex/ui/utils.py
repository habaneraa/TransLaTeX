import aiohttp
import aiofiles
from pathlib import Path


async def adownload(url: str, save_path: Path) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return

            async with aiofiles.open(save_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    await f.write(chunk)


async def copy_files(src_dir: Path, dst_dir: Path) -> None:
    for src_file in src_dir.rglob('*'):
        if src_file.is_file():
            dst_file = dst_dir / src_file.relative_to(src_dir)
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(src_file, 'rb') as src, aiofiles.open(dst_file, 'wb') as dst:
                await dst.write(await src.read())

