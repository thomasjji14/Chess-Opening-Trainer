# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Game.py'],
             pathex=['D:\\Programming\\Chess'],
             binaries=[],
             datas=[('cpieces/*.png', 'cpieces'), ('sfx/*.mp3', 'sfx'), ('engine/sf.exe', 'engine')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Game',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
