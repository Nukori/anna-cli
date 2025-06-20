#!/bin/bash
Delimiter='|' #could not tell you why I did it this way, but I'm too tired to recall presently

#staring at exclusively orange (vscode basic theme because I havent installed catppuccin yet) is very painful.
SELECTED_MD5=$(
	python /home/nukori/things/pystuff/anna.py $@ | awk -v d="$Delimiter" ' 
	BEGIN {
		RS = "\n--- Book [0-9]+ ---\n";
		ORS = "\0" 
	}
	/^--- Printing Raw Book Data ---\n$/ {
		next 
	}

	{
		md5_hash = ""
		metadata = ""
		title = ""
		publisher = ""
		author = ""

		split($0, lines, "\n")
		
		for (i=1; i<=length(lines); i++) {
			if (lines[i] ~ /^MD5:/) {
				md5_hash = substr(lines[i], 6)
			} else if (lines[i] ~ /^Title:/) {
				title = substr(lines[i], 8)
			} else if (lines[i] ~ /^Metadata:/) {
				metadata = substr(lines[i], 11)
			} else if (lines[i] ~ /^Publisher:/) {
				publisher = substr(lines[i], 12)
			} else if (lines[i] ~ /^Author:/) {
				author = substr(lines[i], 9)
			}
		}

		full_display_string = ""
		if (metadata != "") {
			full_display_string = full_display_string "Metadata: " metadata "\n"
		}
		if (title != "") {
			full_display_string = full_display_string "Title: " title "\n"
		}
		if (publisher != "") {
			full_display_string = full_display_string "Publisher: " publisher "\n"
		}
		if (author != "") {
			full_display_string = full_display_string "Author: " author "\n"
		}

		sub(/\n$/, "", full_display_string)

		print md5_hash d full_display_string
	} 
	' | fzf \
	    --read0 \
		--ansi \
		--with-nth=2 \
		--delimiter="$Delimiter" \
		--layout=reverse \
		--gap=2 \
		--highlight-line \
		--multi \
		--nth='..' \
		| cut -d "$DELIMITER" -f 1 | head -c 32
)

#I am aware an ugly amount of the above is hardcoded. No I will not be changing that until some later point this week

if [ -n "$SELECTED_MD5" ]; then
	echo "MD5 of selected title: $SELECTED_MD5"
	read -rp "Download selected title? (Y/n): " -n 1 user_confirmation
	echo 
	DOWNLOAD_URL="https://annas-archive.org/md5/$SELECTED_MD5"
	KEY="" #definitely need to remember to remove this before adding to github
 	#For anyone curious, I still somehow managed to forget to remove this despite adding the comment mere minutes prior.
	DOWNLOAD_URL="https://annas-archive.org/dyn/api/fast_download.json?md5=$SELECTED_MD5&key=$KEY"
	user_confirmation_lc=$(echo "$user_confirmation" | tr '[:upper:]' '[:lower:]')

	if [[ "$user_confirmation_lc" == "y" || -z "$user_confirmation_lc" ]]; then
		echo "Downloading: $DOWNLOAD_URL"
		echo "Heads up: This can take a while, depending on file size and Anna servers."
        json_data=$(wget -qO- "$DOWNLOAD_URL")
		if [ $? -eq 0 ] && [ -n "$json_data" ]; then
			bookDownload=$(echo "$json_data" | jq -r '.download_url')
			file_name=$(wget -nv -t 20 --content-disposition "$bookDownload" 2>&1 | cut -d\" -f2) #code I borrowed from superuser: https://serverfault.com/questions/1156048/use-wget-in-bash-script-how-to-get-downloaded-file-name-using-content-dispos (towards the bottom, the accepted answer.)
			base_name=$(echo "$file_name" | cut -d '-' -f 1 | sed 's/[[:space:]]*$//')
			original_extension=$(echo "$file_name" | grep -o '\.\(epub\|pdf\)\(\.[0-9]\+\)*$' | sed 's/\.[0-9]\+$//')
			if [[ -n "$original_extension" ]]; then
				new_name="${base_name}${original_extension}" #this just looks weird 
				echo "$new_name"
			else
				new_name="${base_name}"
				echo "Warning: No .epub or .pdf extension found in '$file_name'. New name is '$new_name'." #theoretically if i implement proper error handling it will never reach this point, meaning I wasted a bit of time
			fi
			mv "$file_name" "$new_name"
		fi


		
    else
        echo "Download cancelled for $DOWNLOAD_URL"
    fi
else
	echo "No book selected"
fi
