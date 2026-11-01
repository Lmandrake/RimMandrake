os.read of a whole large file through /mnt/c can raise ENOMEM in WSL; 64 KiB chunks did not cure it (it failed again when free memory was 477 MB with 30 GB of page cache); the read has to wait and retry, as deploy_custom_mods._read_retry does. Any hash or compare over the Steam Mods mount needs the same.
home: rimworld-deploy
