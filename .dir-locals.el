((nil . ((projectile-project-compilation-cmd . "cd doc;make html")
	 (projectile-project-run-cmd . "coverage run --source src -m doctest doc/source/tutorial.rst; and coverage html")
	 (projectile-project-test-cmd . "flake8 src; and pylint src")
					     )))
