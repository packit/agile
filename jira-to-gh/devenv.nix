{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [
    gh
  ];

  languages.python = {
    enable = true;
    version = "3.14";
    venv = {
      enable = true;
      requirements = ''
        click
        requests
        tqdm
      '';
    };
  };
}
