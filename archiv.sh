END=246000
num=245510
for ((i=$num;i<=$END;i++)); do
    playlist=$(curl -s "https://www.rtvs.sk/televizia/archiv/16350/$i" | grep -i //www.rtvs.sk/json/archive)
    [[ $playlist ]] && echo $i
    playlist_array=($playlist)
    # Extract playlist link
    playlist_link=$(echo 'https:'${playlist_array[3]} | sed 's/\"//g')
    # echo $playlist_link
    # Extract line with link to stream
    stream_tmp="$(curl -s $playlist_link)"
    # for ((i=1;i<=END;i++)); do
    #     echo $i
    # done
    # echo $stream_tmp

    title=$(jq -r '.clip.title' <<< $stream_tmp)
    [[ $title ]] && echo $title

    # [[ $stream_tmp =~ "Pumpa" ]] && echo "je to PUMPA !"
    # [[ $stream_tmp =~ "Pumpa" ]] && echo $playlist_link
    # [[ $stream_tmp =~ "Pumpa" ]] && echo $playlist
done
