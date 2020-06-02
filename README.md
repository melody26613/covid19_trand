### trend of COVID-19 
##### environment: Ubuntu 16.04 + python3.6

1. fetch data from WHO
2. use polynomial regression to get globally trend of COVID-19
3. can compare with SARS

##### check environment before execute relative python script
$ 0_check_environment.sh

##### fetch WHO data
$ _one_day_fetch.sh

##### automatically fetch WHO data by crontab, fetch data at 11:00 a.m. everyday
$ crontab -e
  0 11 * * * <path of fetch script>_one_day_fetch.sh

update time: 2020/06/01

![image](https://github.com/melody26613/covid19_trend/blob/master/pic/gif/covid19-20200601.gif)

![image](https://github.com/melody26613/covid19_trend/blob/master/pic/sars.jpg)
