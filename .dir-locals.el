((nil . ((projectile-project-compilation-cmd . "cd doc;make html")
	 (projectile-project-run-cmd . "python -m doctest doc/source/tutorial.rst")
	 (projectile-project-test-cmd . "flake8 src; and pylint src")
					     )))
