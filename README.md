<a href="https://marvelapp.com/31dgaj4/screen/17384930">
    <img src="C:\Users\jbadiabo\Pictures\BetonSibyl\Sibyl_white_logo.png" alt="Sibyl logo" title="Sibyl" align="right" height="60" />
</a>

Sport Predictions Project - Bet on Sibyl 
======================
### Bet on Sibyl in a nutshell

BetonSibyl is a platform controlled by a set of algorithmic models (a model defined for each sport)
that projects accurately estimated results (predictions of upcoming games) from a multitude of statistical variables.
At launch, the platform will cover the four major US sports, soccer and tennis. Moreover, the models provide stats to measure the
performance of the algorithm for the current season (for each sport) along with bankroll comparaison stats with bookmaker 
(scraping from the [oddsportal's website](http://www.oddsportal.com/) to do so)

[![Aimeos TYPO3 demo](C:\Users\jbadiabo\Pictures\Sibyl_mobile_app_screenshots.png)](https://marvelapp.com/31dgaj4/screen/17384930)

## Table of content

- [Data collection](#data-collection)
    - [Decomposition - Data Design Decisions](#data-design-decisions)
    - [Web Scraping - Selenium/Beautiful Soup](#web-scraping)
- [Predictions](#predictions)
    - [Data Preprocessing](#data-preprocessing)
    - [Algorithm Tuning and Running](#algorithm-tuning-and-runing)
- [Results Presentation](#results-presentation)
    - [Bookmakers comparaison over the year](#bookmakers-comparaison-over-the-year)
    - [Model Performance Metrics](#model-performance-metrics)
    - [ML one-sport process in a nutshell](#ml-one-sport-process-in-a-nutshell)
- [License](#license)
- [Links](#links)

## Data collection

### Data Design Decisions

If you want to install Aimeos into your existing TYPO3 installation, the [Aimeos extension from the TER](https://typo3.org/extensions/repository/view/aimeos) is recommended. You can download and install it directly from the Extension Manager of your TYPO3 instance.

For new TYPO3 installations, there's a 1-click [Aimeos distribution](https://typo3.org/extensions/repository/view/aimeos_dist) available too. Choose the Aimeos distribution from the list of available distributions in the Extension Manager and you will get a completely set up shop system including demo data for a quick start.

### Web Scraping

The latest version can be installed via composer too. This is especially useful if you want to create new TYPO3 installations automatically or play with the latest code. You need to install the [composer](https://getcomposer.org/) package first if it isn't already available:
```
php -r "readfile('https://getcomposer.org/installer');" | php -- --filename=composer
```

In order to tell composer what it should install, you have to create a basic `composer.json` file in the directory of you VHost. It should look similar to this one:
```json
{
    "name": "vendor/mysite",
    "description" : "My new TYPO3 web site",
    "minimum-stability": "dev",
    "prefer-stable": true,
    "repositories": [
        { "type": "composer", "url": "https://composer.typo3.org/" }
    ],
    "require": {
        "typo3/cms": "~7.6",
        "aimeos/aimeos-typo3": "dev-master"
    },
    "extra": {
        "typo3/cms": {
            "cms-package-dir": "{$vendor-dir}/typo3/cms",
            "web-dir": "htdocs"
        }
    },
    "scripts": {
        "post-install-cmd": [
            "Aimeos\\Aimeos\\Custom\\Composer::install"
        ],
        "post-update-cmd": [
            "Aimeos\\Aimeos\\Custom\\Composer::install"
        ]
    }
}
```
It will install TYPO3 and the latest Aimeos TYPO3 extension in the `./htdocs/` directory. Afterwards, the Aimeos composer script will be executed which copies some required files and adds a link to the Aimeos extensions placed in the `./ext/` directory. To start installation, execute composer on the command line in the directory where your `composer.json` is stored:
```
composer update
```

## Predictions

### Data preprocessing

* Log into the TYPO3 back end
* Click on ''Admin Tools::Extension Manager'' in the left navigation
* Click the icon with the little plus sign left from the Aimeos list entry (looks like a lego brick)
* If a pop-up opens (only TYPO3 4.x) choose ''Make updates'' and "Close window" after the installation is done

**Caution:** Install the **RealURL extension before the Aimeos extension** to get nice looking URLs. Otherwise, RealURL doesn't rewrite the parameters even if you install RealURL afterwards!

![Install Aimeos TYPO3 extension](https://aimeos.org/docs/images/Aimeos-typo3-extmngr-install.png)

### Algorithm Tuning and Running

Afterwards, you have to execute the update script of the extension to create the required database structure:

![Execute update script](https://aimeos.org/docs/images/Aimeos-typo3-extmngr-update-7.x.png)

## Results Presentation

The page setup for an Aimeos web shop is easy if you import the [standard page tree](https://aimeos.org/fileadmin/download/Aimeos-pages_two-columns_2.1.6.t3d) into your TYPO3 installation.

### Bookmakers comparaison over the year

* In Web::Page, root page (the one with the globe)
* Right click on the globe
* Move the cursor to "Branch actions"
* In the sub-menu, click on "Import from .t3d"

![Go to the import view](https://aimeos.org/docs/images/Aimeos-typo3-pages-menu.png)

### Model Performance Metrics

* In the page import dialog
* Select the "Upload" tab (2nd one)
* Click on the "Select" dialog
* Choose the file you've downloaded
* Press the "Upload files" button

![Upload the page tree file](https://aimeos.org/docs/images/Aimeos-typo3-pages-upload.png)

### ML one-sport process in a nutshell

* In Import / Export view
* Select the uploaded file from the drop-down menu
* Click on the "Preview" button
* The pages that will be imported are shown below
* Click on the "Import" button that has appeared
* Confirm to import the pages

![Import the uploaded page tree file](https://aimeos.org/docs/images/Aimeos-typo3-pages-import.png)

Now you have a new page "Shop" in your page tree including all required sub-pages.

## License

The Aimeos TYPO3 extension is licensed under the terms of the GPL Open Source
license and is available for free.

## Links

* [Web site](https://aimeos.org/integrations/typo3-shop-extension/)
* [Documentation](https://aimeos.org/docs/TYPO3)
* [Forum](https://aimeos.org/help/typo3-extension-f16/)
* [Issue tracker](https://github.com/aimeos/aimeos-typo3/issues)
* [Source code](https://github.com/aimeos/aimeos-typo3)
