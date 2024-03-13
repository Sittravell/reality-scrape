All of this should run from root folder. Root folder is the directory above app folder.

Python Env

Run:
conda activate arvrnews


Scrape

Run:
python -m app.scraper.main


Api

Setup:
1. Clone repository
cd ~/domains/realityrumor.com/
git config --global credential.helper store  //This is needed so that you dont key in password everytime
git clone https://sittravell@bitbucket.org/sittravell/arvrnews-api.git
Type the password

2. Install composer 2.5:
NOTE!: It is best to check the composer website for installation instructions. Just make sure install it in the directory mentioned.
cd ~/domains/realityrumor.com
php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
php -r "if (hash_file('sha384', 'composer-setup.php') === '55ce33d7678c5a611085589f1f3ddf8b3c52d662cd01d4ba75c0ee0459970c2200a51f492d557530c71c15d8dba01eae') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
php composer-setup.php
php -r "unlink('composer-setup.php');"

3. Generate laravel project
cd ~/domains/realityrumor.com/arvrnews-api
/opt/alt/php81/usr/bin/php ../composer.phar update

4. Update .env
cd ~/domains/realityrumor.com/arvrnews-api
nano .env
//Change APP_NAME
//Remove APP_KEY, ONLY THE VALUE!
//Change DB conf to Hostinger's DB conf

5. Generate key and create db
cd ~/domains/realityrumor.com/arvrnews-api
/opt/alt/php81/usr/bin/php artisan key:generate
/opt/alt/php81/usr/bin/php artisan migrate

6. Move all public files to public_html
cd ~/domains/realityrumor.com/
Remove all files in public_html
mv arvrnews-api/public/* public_html/   //find a way to move .htaccess together, im noob lol
mv arvrnews-api/public/.htaccess public_html/    

7. Modify index.php
nano ~/domains/realityrumor.com/public_html/index.php
Change all paths in index.php from /../some_folder... to /../arvrnews-api/some_folder...

8. Make sure php version is 8.1^
Hosting > realityrumor.com > Advanced > PHP Configuration
Choose PHP 8.1 or above
Click update

You should be good to go..


Alembic 

Create new version:
alembic revision --autogenerate -m "message"

Commit the version:
alembic upgrade head

Rollback 1 version:
alembic downgrade -1


AWS

Connect to ec2 instance
cd to directory that have arvrnews.pem
chmod 400 arvrnews.pem (only done once)
ssh -i "arvrnews.pem" ubuntu@ec2-100-26-239-113.compute-1.amazonaws.com

SSH
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/avn-bb

Conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate arvrnews