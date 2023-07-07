#!/bin/bash

while [[ -n $1 ]];
	[[ $(( $1 % 4 )) = 0 ]] && i=1 || i=0
       	# echo $i	
	[[ $i = 1 ]] && [[ $(( $1 % 100 )) = 0 ]] && i=1 || [[ $i = 0 ]] || i=2
	# echo $i
	[[ $i = 1 ]] && [[ $(( $1 % 400 )) = 0 ]] && i=2
	# echo $i
	[[ $i = 2 ]] &&  echo "True $1" || echo "False $1"
	

	shift
done

exit 42