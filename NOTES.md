- What you found (root cause of each bug)
line 149 and 150 was not using the Dead zone but 0
line 140 to 146 did not change the frame

- What you fixed and why
Changed line 149 and 150 to use the dz_half_w/h
Changed line 140 to 146 to include changing the frame

- Any design decisions in your debouncer implementation
I decided to create the (track_id, start, length) in list first so I can change it when I need to replace the id if the len is too short and then made it into a tuple after replacement. I also decide to create a None list first when creating the final output as I could check the id if it exists before updating it so maybe lessen the time it takes to create the output list if theres alot if None ids.

- Anything else you noticed or would improve given more time
I would have tested my code with other testcases but I struggled to install opencv so I could not finish in time
