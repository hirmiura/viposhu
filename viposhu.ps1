$env:Path = `
   $env:PYENV_ROOT + "bin;" `
 + $env:PYENV_ROOT + "shims;" `
+ "$env:APPDATA\Python\Scripts;" `
 + $env:Path

poetry run python -m viposhu

pause