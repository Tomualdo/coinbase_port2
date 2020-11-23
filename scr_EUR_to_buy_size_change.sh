find . -name "*strategy.json" | xargs grep "EUR_to_buy_size"
[ -z $1 ] || [ -z $2 ] && echo "Change EUR_to_buy_size from <ARG1> to <ARG2>" && exit 1
find . -name "*strategy.json" | xargs sed -i "s/\"EUR_to_buy_size\": $1/\"EUR_to_buy_size\": $2/g"
find . -name "*strategy.json" | xargs grep "EUR_to_buy_size"
