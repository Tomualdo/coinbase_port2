find . -name "*strategy.json" | xargs grep "min_buy_time_minutes"
[ -z $1 ] || [ -z $2 ] && echo "Change min_buy_time_minutes from <ARG1> to <ARG2>" && exit 1
find . -name "*strategy.json" | xargs sed -i "s/\"min_buy_time_minutes\": $1/\"min_buy_time_minutes\": $2/g"
find . -name "*strategy.json" | xargs grep "min_buy_time_minutes"
