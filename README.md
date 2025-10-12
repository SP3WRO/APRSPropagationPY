APRS_propagation.py is used to transmit information about propagation conditions in the 2 m band.

How it works:
Every 15 minutes, the script retrieves the “text_display” data from the website vhf.dxview.org and checks whether APRS frames have exceeded distances of 250 km and 500 km for gridsquares located within the borders of Poland. After analysis, it reports either “enhanced propagation” or “very high propagation.” The data are then formatted into an APRS frame and sent using the KISS protocol over TCP.

In my setup, I use a radio with the VP-DIGI digipeater connected to the computer. The computer runs share-tnc and aprx (for iGate) to exchange information between them.

The script can be freely customized to individual needs.
The project is installed on station SR3WR.

