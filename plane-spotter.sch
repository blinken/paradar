v 20130925 2
C 40000 40000 0 0 0 title-B.sym
C 42800 45300 1 0 0 raspberry-pi-rev2-p1.sym
{
T 43100 48500 5 10 1 1 0 0 1
refdes=U1
T 43100 48700 5 10 0 0 0 0 1
footprint=HEADER40_2
T 43100 48100 5 10 1 1 0 0 1
description=Raspberry Pi Model B Rev 2 P1
T 43100 48300 5 10 1 1 0 0 1
value=TBD
}
C 55100 44000 1 0 0 connector12-2.sym
{
T 55800 49300 5 10 1 1 0 6 1
refdes=GPS1
T 55400 49250 5 10 0 0 0 0 1
device=CONNECTOR_12
T 55400 49450 5 10 0 0 0 0 1
footprint=quectel-l86-gps-receiver
}
C 53100 47400 1 180 0 capacitor-2.sym
{
T 52900 46700 5 10 0 0 180 0 1
device=POLARIZED_CAPACITOR
T 52900 46900 5 10 1 1 180 0 1
refdes=C3
T 52900 46500 5 10 0 0 180 0 1
symversion=0.1
T 53100 47400 5 10 1 1 0 0 1
value=220mF
T 53100 47400 5 10 0 0 0 0 1
footprint=EECRG0V224HN-panasonic-supercap-horizontal
}
C 53200 47200 1 90 0 resistor-1.sym
{
T 52800 47500 5 10 0 0 90 0 1
device=RESISTOR
T 52900 47400 5 10 1 1 90 0 1
refdes=R1
T 53200 47200 5 10 1 1 0 0 1
value=4.7k
T 53200 47200 5 10 0 0 0 0 1
footprint=1206
}
C 50900 45900 1 90 0 capacitor-1.sym
{
T 50200 46100 5 10 0 0 90 0 1
device=CAPACITOR
T 50400 46100 5 10 1 1 90 0 1
refdes=C2
T 50000 46100 5 10 0 0 90 0 1
symversion=0.1
T 50900 45900 5 10 1 1 0 0 1
value=100n
T 50900 45900 5 10 0 0 0 0 1
footprint=1206
}
C 49500 46800 1 270 0 capacitor-2.sym
{
T 50200 46600 5 10 0 0 270 0 1
device=POLARIZED_CAPACITOR
T 50000 46600 5 10 1 1 270 0 1
refdes=C1
T 50400 46600 5 10 0 0 270 0 1
symversion=0.1
T 49500 46800 5 10 1 1 0 0 1
value=47u
T 49500 46800 5 10 0 0 0 0 1
footprint=1206
}
N 53400 46800 55100 46800 4
N 55100 48000 54700 48000 4
{
T 55000 48000 5 10 1 1 0 0 1
netname=0V
}
N 53500 47600 55100 47600 4
{
T 54900 47600 5 10 1 1 0 0 1
netname=3V3
}
N 55100 47200 53100 47200 4
N 53500 47600 53500 48100 4
N 51500 48100 53500 48100 4
N 49700 45900 53400 45900 4
{
T 49700 45900 5 10 1 1 0 0 1
netname=0V
}
N 52200 47200 52200 45900 4
N 49700 46800 51500 46800 4
N 51500 46800 51500 48100 4
N 42800 45400 42400 45400 4
{
T 42500 45400 5 10 1 1 0 0 1
netname=0V
}
N 42800 46200 42400 46200 4
{
T 42500 46200 5 10 1 1 0 0 1
netname=3V3
}
N 42800 47000 42400 47000 4
{
T 42500 47000 5 10 1 1 0 0 1
netname=0V
}
N 42800 47800 42400 47800 4
{
T 42500 47800 5 10 1 1 0 0 1
netname=3V3
}
N 45500 47800 45900 47800 4
{
T 46100 47900 5 10 1 1 0 0 1
netname=5V0
}
N 45500 47600 45900 47600 4
{
T 45800 47600 5 10 1 1 0 0 1
netname=5V0
}
N 45500 47400 45900 47400 4
{
T 45800 47400 5 10 1 1 0 0 1
netname=0V
}
N 45500 46600 45900 46600 4
{
T 45800 46600 5 10 1 1 0 0 1
netname=0V
}
N 45500 46000 45900 46000 4
{
T 45800 46000 5 10 1 1 0 0 1
netname=0V
}
N 45500 47000 51300 47000 4
N 51300 47000 51300 48400 4
N 51300 48400 55100 48400 4
N 45500 47200 51100 47200 4
N 51100 47200 51100 48800 4
N 51100 48800 55100 48800 4
N 45500 46400 46300 46400 4
{
T 46200 46400 5 10 1 1 0 0 1
netname=COMPASS_DRDY
}
N 45500 46200 46300 46200 4
{
T 46300 46200 5 10 1 1 0 0 1
netname=COMPASS_CS
}
N 45500 46800 46300 46800 4
{
T 46300 46800 5 10 1 1 0 0 1
netname=PIXEL_PWM
}
N 45500 45800 49400 45800 4
N 49400 45800 49400 45600 4
N 49400 45600 53900 45600 4
N 53900 45600 53900 46400 4
N 53900 46400 55100 46400 4
{
T 54500 46400 5 10 1 1 0 0 1
netname=GPS_FORCE_ON
}
N 55100 44400 54700 44400 4
{
T 54700 44400 5 10 1 1 0 0 1
netname=0V
}
N 55100 45200 54100 45200 4
{
T 54200 45200 5 10 1 1 0 0 1
netname=GPS_RESET
}
N 42800 46800 41800 46800 4
{
T 42000 46800 5 10 1 1 0 0 1
netname=GPS_RESET
}
C 47000 40800 1 0 0 connector8-2.sym
{
T 47700 44500 5 10 1 1 0 6 1
refdes=COMPASS1
T 47300 44450 5 10 0 0 0 0 1
device=CONNECTOR_8
T 47300 44650 5 10 0 0 0 0 1
footprint=rm3100-compass
}
N 47000 44000 46300 44000 4
{
T 46500 44000 5 10 1 1 0 0 1
netname=3V3
}
N 47000 43600 46200 43600 4
{
T 46500 43600 5 10 1 1 0 0 1
netname=0V
}
N 47000 42400 46300 42400 4
{
T 46500 42400 5 10 1 1 0 0 1
netname=SPI_SCLK
}
N 47000 42000 46300 42000 4
{
T 46500 42000 5 10 1 1 0 0 1
netname=SPI_MOSI
}
N 47000 41600 46300 41600 4
{
T 46600 41600 5 10 1 1 0 0 1
netname=SPI_MISO
}
N 47000 41200 46300 41200 4
{
T 46600 41200 5 10 1 1 0 0 1
netname=COMPASS_CS
}
N 46300 42800 47000 42800 4
{
T 46600 42800 5 10 1 1 0 0 1
netname=COMPASS_DRDY
}
N 42800 46000 41800 46000 4
{
T 42000 46000 5 10 1 1 0 0 1
netname=SPI_MOSI
}
N 42800 45800 41800 45800 4
{
T 42100 45800 5 10 1 1 0 0 1
netname=SPI_MISO
}
N 42800 45600 41800 45600 4
{
T 42100 45600 5 10 1 1 0 0 1
netname=SPI_SCLK
}
C 62000 48100 1 0 0 connector6-2.sym
{
T 62700 51000 5 10 1 1 0 6 1
refdes=PX1
T 62300 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 62300 51150 5 10 0 1 0 0 1
footprint=WS2813
}
C 64300 48100 1 0 0 connector6-2.sym
{
T 65000 51000 5 10 1 1 0 6 1
refdes=PX2
T 64600 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 64600 51150 5 10 0 1 0 0 1
footprint=WS2813
}
C 66500 48100 1 0 0 connector6-2.sym
{
T 67200 51000 5 10 1 1 0 6 1
refdes=PX3
T 66800 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 66800 51150 5 10 0 1 0 0 1
footprint=WS2813
}
C 68800 48100 1 0 0 connector6-2.sym
{
T 69500 51000 5 10 1 1 0 6 1
refdes=PX4
T 69100 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 69100 51150 5 10 0 1 0 0 1
footprint=WS2813
}
C 71000 48100 1 0 0 connector6-2.sym
{
T 71700 51000 5 10 1 1 0 6 1
refdes=PX5
T 71300 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 71300 51150 5 10 0 1 0 0 1
footprint=WS2813
}
C 73200 48100 1 0 0 connector6-2.sym
{
T 73900 51000 5 10 1 1 0 6 1
refdes=PX6
T 73500 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 73500 51150 5 10 0 1 0 0 1
footprint=WS2813
}
N 62000 50100 61600 50100 4
N 61600 50100 61600 52800 4
N 73200 50100 73000 50100 4
N 73000 50100 73000 52100 4
N 73000 52100 61600 52100 4
{
T 72900 52100 5 10 1 1 0 0 1
netname=5V0
}
N 64300 50100 64100 50100 4
N 64100 50100 64100 52100 4
N 66500 50100 66300 50100 4
N 66300 50100 66300 52100 4
N 68800 50100 68600 50100 4
N 68600 50100 68600 52100 4
N 71000 50100 70800 50100 4
N 70800 50100 70800 52100 4
N 60100 49300 62000 49300 4
{
T 60100 49300 5 10 1 1 0 0 1
netname=PIXEL_PWM
}
N 62000 48900 61300 48900 4
N 61300 48500 61300 51800 4
N 59900 51800 72700 51800 4
{
T 61300 51800 5 10 1 1 0 0 1
netname=0V
}
N 72700 51800 72700 48900 4
N 72700 48900 73200 48900 4
N 64300 48900 63800 48900 4
N 63800 48900 63800 51800 4
N 66500 48900 66000 48900 4
N 66000 48900 66000 51800 4
N 68800 48900 68300 48900 4
N 68300 48900 68300 51800 4
N 71000 48900 70500 48900 4
N 70500 48900 70500 51800 4
N 62000 49700 61000 49700 4
N 61000 49700 61000 51500 4
N 61000 51500 63500 51500 4
N 63500 47500 63500 51500 4
N 63500 49300 64300 49300 4
N 64300 49700 63200 49700 4
N 63200 49700 63200 51200 4
N 63200 51200 65700 51200 4
N 65700 47800 65700 51200 4
N 65700 49300 66500 49300 4
N 66500 49700 65400 49700 4
N 65400 49700 65400 51500 4
N 65400 51500 68000 51500 4
N 68000 47500 68000 51500 4
N 68000 49300 68800 49300 4
N 68800 49700 67700 49700 4
N 67700 49700 67700 51200 4
N 67700 51200 70200 51200 4
N 70200 47800 70200 51200 4
N 70200 49300 71000 49300 4
N 71000 49700 69900 49700 4
N 69900 49700 69900 51500 4
N 69900 51500 72400 51500 4
N 72400 47500 72400 51500 4
N 72400 49300 73200 49300 4
N 73200 49700 72000 49700 4
N 72000 49700 72000 51200 4
N 72000 51200 76100 51200 4
N 62000 48500 61300 48500 4
N 61000 49300 61000 47800 4
N 61000 47800 64300 47800 4
N 64300 47800 64300 48500 4
N 63500 47500 66500 47500 4
N 66500 47500 66500 48500 4
N 65700 47800 68800 47800 4
N 68800 47800 68800 48500 4
N 68000 47500 71000 47500 4
N 71000 47500 71000 48500 4
N 70200 47800 73200 47800 4
N 73200 47800 73200 48500 4
N 72400 47500 77400 47500 4
C 77400 48100 1 0 0 connector6-2.sym
{
T 77700 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 77700 51150 5 10 0 1 0 0 1
footprint=WS2813
T 78100 51000 5 10 1 1 0 6 1
refdes=PX7
}
C 79700 48100 1 0 0 connector6-2.sym
{
T 80000 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 80000 51150 5 10 0 1 0 0 1
footprint=WS2813
T 80400 51000 5 10 1 1 0 6 1
refdes=PX8
}
C 81900 48100 1 0 0 connector6-2.sym
{
T 82200 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 82200 51150 5 10 0 1 0 0 1
footprint=WS2813
T 82600 51000 5 10 1 1 0 6 1
refdes=PX9
}
C 84200 48100 1 0 0 connector6-2.sym
{
T 84500 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 84500 51150 5 10 0 1 0 0 1
footprint=WS2813
T 84900 51000 5 10 1 1 0 6 1
refdes=PX10
}
C 86400 48100 1 0 0 connector6-2.sym
{
T 86700 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 86700 51150 5 10 0 1 0 0 1
footprint=WS2813
T 87100 51000 5 10 1 1 0 6 1
refdes=PX11
}
C 88600 48100 1 0 0 connector6-2.sym
{
T 88900 50950 5 10 0 0 0 0 1
device=CONNECTOR_6
T 88900 51150 5 10 0 1 0 0 1
footprint=WS2813
T 89300 51000 5 10 1 1 0 6 1
refdes=PX12
}
N 77400 50100 77000 50100 4
N 77000 50100 77000 52700 4
N 88600 50100 88400 50100 4
N 88400 50100 88400 52100 4
N 88400 52100 77000 52100 4
{
T 88300 52100 5 10 1 1 0 0 1
netname=5V0
}
N 79700 50100 79500 50100 4
N 79500 50100 79500 52100 4
N 81900 50100 81700 50100 4
N 81700 50100 81700 52100 4
N 84200 50100 84000 50100 4
N 84000 50100 84000 52100 4
N 86400 50100 86200 50100 4
N 86200 50100 86200 52100 4
N 77400 48900 76700 48900 4
N 76700 48900 76700 51800 4
N 75700 51800 88100 51800 4
{
T 76700 51800 5 10 1 1 0 0 1
netname=0V
}
N 88100 51800 88100 48900 4
N 88100 48900 88600 48900 4
N 79700 48900 79200 48900 4
N 79200 48900 79200 51800 4
N 81900 48900 81400 48900 4
N 81400 48900 81400 51800 4
N 84200 48900 83700 48900 4
N 83700 48900 83700 51800 4
N 86400 48900 85900 48900 4
N 85900 48900 85900 51800 4
N 77400 49700 76400 49700 4
N 76400 49700 76400 51500 4
N 76400 51500 78900 51500 4
N 78900 47500 78900 51500 4
N 78900 49300 79700 49300 4
N 79700 49700 78600 49700 4
N 78600 49700 78600 51200 4
N 78600 51200 81100 51200 4
N 81100 47800 81100 51200 4
N 81100 49300 81900 49300 4
N 81900 49700 80800 49700 4
N 80800 49700 80800 51500 4
N 80800 51500 83400 51500 4
N 83400 47500 83400 51500 4
N 83400 49300 84200 49300 4
N 84200 49700 83100 49700 4
N 83100 49700 83100 51200 4
N 83100 51200 85600 51200 4
N 85600 47800 85600 51200 4
N 85600 49300 86400 49300 4
N 86400 49700 85300 49700 4
N 85300 49700 85300 51500 4
N 85300 51500 87800 51500 4
N 87800 47200 87800 51500 4
N 87800 49300 88600 49300 4
N 88600 49700 87400 49700 4
N 87400 49700 87400 51200 4
N 87400 51200 89900 51200 4
N 76400 49300 76400 47800 4
N 76400 47800 79700 47800 4
N 79700 47800 79700 48500 4
N 78900 47500 81900 47500 4
N 81900 47500 81900 48500 4
N 81100 47800 84200 47800 4
N 84200 47800 84200 48500 4
N 83400 47500 86400 47500 4
N 86400 47500 86400 48500 4
N 85600 47800 88600 47800 4
N 88600 47800 88600 48500 4
N 77400 47500 77400 48500 4
N 76100 51200 76100 49300 4
N 76100 49300 77400 49300 4
C 62000 41700 1 0 0 connector6-2.sym
{
T 62300 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 62300 44750 5 10 0 1 0 0 1
footprint=WS2813
T 62700 44600 5 10 1 1 0 6 1
refdes=PX13
}
C 64300 41700 1 0 0 connector6-2.sym
{
T 64600 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 64600 44750 5 10 0 1 0 0 1
footprint=WS2813
T 65000 44600 5 10 1 1 0 6 1
refdes=PX14
}
C 66500 41700 1 0 0 connector6-2.sym
{
T 66800 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 66800 44750 5 10 0 1 0 0 1
footprint=WS2813
T 67200 44600 5 10 1 1 0 6 1
refdes=PX15
}
C 68800 41700 1 0 0 connector6-2.sym
{
T 69100 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 69100 44750 5 10 0 1 0 0 1
footprint=WS2813
T 69500 44600 5 10 1 1 0 6 1
refdes=PX16
}
C 71000 41700 1 0 0 connector6-2.sym
{
T 71300 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 71300 44750 5 10 0 1 0 0 1
footprint=WS2813
T 71700 44600 5 10 1 1 0 6 1
refdes=PX17
}
C 73200 41700 1 0 0 connector6-2.sym
{
T 73500 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 73500 44750 5 10 0 1 0 0 1
footprint=WS2813
T 73900 44600 5 10 1 1 0 6 1
refdes=PX18
}
N 62000 43700 61600 43700 4
N 61600 43700 61600 46300 4
N 73200 43700 73000 43700 4
N 73000 43700 73000 45700 4
N 73000 45700 61600 45700 4
{
T 72900 45700 5 10 1 1 0 0 1
netname=5V0
}
N 64300 43700 64100 43700 4
N 64100 43700 64100 45700 4
N 66500 43700 66300 43700 4
N 66300 43700 66300 45700 4
N 68800 43700 68600 43700 4
N 68600 43700 68600 45700 4
N 71000 43700 70800 43700 4
N 70800 43700 70800 45700 4
N 59400 42900 62000 42900 4
N 62000 42500 61300 42500 4
N 61300 42500 61300 45400 4
N 60500 45400 72700 45400 4
{
T 61300 45400 5 10 1 1 0 0 1
netname=0V
}
N 72700 45400 72700 42500 4
N 72700 42500 73200 42500 4
N 64300 42500 63800 42500 4
N 63800 42500 63800 45400 4
N 66500 42500 66000 42500 4
N 66000 42500 66000 45400 4
N 68800 42500 68300 42500 4
N 68300 42500 68300 45400 4
N 71000 42500 70500 42500 4
N 70500 42500 70500 45400 4
N 62000 43300 61000 43300 4
N 61000 43300 61000 45100 4
N 61000 45100 63500 45100 4
N 63500 41100 63500 45100 4
N 63500 42900 64300 42900 4
N 64300 43300 63200 43300 4
N 63200 43300 63200 44800 4
N 63200 44800 65700 44800 4
N 65700 41400 65700 44800 4
N 65700 42900 66500 42900 4
N 66500 43300 65400 43300 4
N 65400 43300 65400 45100 4
N 65400 45100 68000 45100 4
N 68000 41100 68000 45100 4
N 68000 42900 68800 42900 4
N 68800 43300 67700 43300 4
N 67700 43300 67700 44800 4
N 67700 44800 70200 44800 4
N 70200 41400 70200 44800 4
N 70200 42900 71000 42900 4
N 71000 43300 69900 43300 4
N 69900 43300 69900 45100 4
N 69900 45100 72400 45100 4
N 72400 41100 72400 45100 4
N 72400 42900 73200 42900 4
N 73200 43300 72000 43300 4
N 72000 43300 72000 44800 4
N 72000 44800 76100 44800 4
N 61000 42900 61000 41400 4
N 61000 41400 64300 41400 4
N 64300 41400 64300 42100 4
N 63500 41100 66500 41100 4
N 66500 41100 66500 42100 4
N 65700 41400 68800 41400 4
N 68800 41400 68800 42100 4
N 68000 41100 71000 41100 4
N 71000 41100 71000 42100 4
N 70200 41400 73200 41400 4
N 73200 41400 73200 42100 4
N 72400 41100 77400 41100 4
C 77400 41700 1 0 0 connector6-2.sym
{
T 77700 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 77700 44750 5 10 0 1 0 0 1
footprint=WS2813
T 78100 44600 5 10 1 1 0 6 1
refdes=PX19
}
C 79700 41700 1 0 0 connector6-2.sym
{
T 80000 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 80000 44750 5 10 0 1 0 0 1
footprint=WS2813
T 80400 44600 5 10 1 1 0 6 1
refdes=PX20
}
C 81900 41700 1 0 0 connector6-2.sym
{
T 82200 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 82200 44750 5 10 0 1 0 0 1
footprint=WS2813
T 82600 44600 5 10 1 1 0 6 1
refdes=PX21
}
C 84200 41700 1 0 0 connector6-2.sym
{
T 84500 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 84500 44750 5 10 0 1 0 0 1
footprint=WS2813
T 84900 44600 5 10 1 1 0 6 1
refdes=PX22
}
C 86400 41700 1 0 0 connector6-2.sym
{
T 86700 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 86700 44750 5 10 0 1 0 0 1
footprint=WS2813
T 87100 44600 5 10 1 1 0 6 1
refdes=PX23
}
C 88600 41700 1 0 0 connector6-2.sym
{
T 88900 44550 5 10 0 0 0 0 1
device=CONNECTOR_6
T 88900 44750 5 10 0 1 0 0 1
footprint=WS2813
T 89300 44600 5 10 1 1 0 6 1
refdes=PX24
}
N 77400 43700 77000 43700 4
N 77000 43700 77000 46300 4
N 88600 43700 88400 43700 4
N 88400 43700 88400 45700 4
N 88400 45700 77000 45700 4
{
T 88300 45700 5 10 1 1 0 0 1
netname=5V0
}
N 79700 43700 79500 43700 4
N 79500 43700 79500 45700 4
N 81900 43700 81700 43700 4
N 81700 43700 81700 45700 4
N 84200 43700 84000 43700 4
N 84000 43700 84000 45700 4
N 86400 43700 86200 43700 4
N 86200 43700 86200 45700 4
N 77400 42500 76700 42500 4
N 76700 42500 76700 45400 4
N 76000 45400 88100 45400 4
{
T 76700 45400 5 10 1 1 0 0 1
netname=0V
}
N 88100 45400 88100 42500 4
N 88100 42500 88600 42500 4
N 79700 42500 79200 42500 4
N 79200 42500 79200 45400 4
N 81900 42500 81400 42500 4
N 81400 42500 81400 45400 4
N 84200 42500 83700 42500 4
N 83700 42500 83700 45400 4
N 86400 42500 85900 42500 4
N 85900 42500 85900 45400 4
N 77400 43300 76400 43300 4
N 76400 43300 76400 45100 4
N 76400 45100 78900 45100 4
N 78900 41100 78900 45100 4
N 78900 42900 79700 42900 4
N 79700 43300 78600 43300 4
N 78600 43300 78600 44800 4
N 78600 44800 81100 44800 4
N 81100 41400 81100 44800 4
N 81100 42900 81900 42900 4
N 81900 43300 80800 43300 4
N 80800 43300 80800 45100 4
N 80800 45100 83400 45100 4
N 83400 41100 83400 45100 4
N 83400 42900 84200 42900 4
N 84200 43300 83100 43300 4
N 83100 43300 83100 44800 4
N 83100 44800 85600 44800 4
N 85600 41400 85600 44800 4
N 85600 42900 86400 42900 4
N 86400 43300 85300 43300 4
N 85300 43300 85300 45100 4
N 85300 45100 87800 45100 4
N 87800 40800 87800 45100 4
N 87800 42900 88600 42900 4
N 88600 43300 87400 43300 4
N 87400 43300 87400 44800 4
N 87400 44800 89900 44800 4
N 76400 42900 76400 41400 4
N 76400 41400 79700 41400 4
N 79700 41400 79700 42100 4
N 78900 41100 81900 41100 4
N 81900 41100 81900 42100 4
N 81100 41400 84200 41400 4
N 84200 41400 84200 42100 4
N 83400 41100 86400 41100 4
N 86400 41100 86400 42100 4
N 85600 41400 88600 41400 4
N 88600 41400 88600 42100 4
N 77400 41100 77400 42100 4
N 76100 44800 76100 42900 4
N 76100 42900 77400 42900 4
C 62000 35300 1 0 0 connector6-2.sym
{
T 62300 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 62300 38350 5 10 0 1 0 0 1
footprint=WS2813
T 62700 38200 5 10 1 1 0 6 1
refdes=PX25
}
C 64300 35300 1 0 0 connector6-2.sym
{
T 64600 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 64600 38350 5 10 0 1 0 0 1
footprint=WS2813
T 65000 38200 5 10 1 1 0 6 1
refdes=PX26
}
C 66500 35300 1 0 0 connector6-2.sym
{
T 66800 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 66800 38350 5 10 0 1 0 0 1
footprint=WS2813
T 67200 38200 5 10 1 1 0 6 1
refdes=PX27
}
C 68800 35300 1 0 0 connector6-2.sym
{
T 69100 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 69100 38350 5 10 0 1 0 0 1
footprint=WS2813
T 69500 38200 5 10 1 1 0 6 1
refdes=PX28
}
C 71000 35300 1 0 0 connector6-2.sym
{
T 71300 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 71300 38350 5 10 0 1 0 0 1
footprint=WS2813
T 71700 38200 5 10 1 1 0 6 1
refdes=PX29
}
C 73200 35300 1 0 0 connector6-2.sym
{
T 73500 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 73500 38350 5 10 0 1 0 0 1
footprint=WS2813
T 73900 38200 5 10 1 1 0 6 1
refdes=PX30
}
N 62000 37300 61600 37300 4
N 61600 37300 61600 40000 4
N 73200 37300 73000 37300 4
N 73000 37300 73000 39300 4
N 73000 39300 61600 39300 4
{
T 72900 39300 5 10 1 1 0 0 1
netname=5V0
}
N 64300 37300 64100 37300 4
N 64100 37300 64100 39300 4
N 66500 37300 66300 37300 4
N 66300 37300 66300 39300 4
N 68800 37300 68600 37300 4
N 68600 37300 68600 39300 4
N 71000 37300 70800 37300 4
N 70800 37300 70800 39300 4
N 59400 36500 62000 36500 4
N 62000 36100 61300 36100 4
N 61300 36100 61300 39000 4
N 60400 39000 72700 39000 4
{
T 61300 39000 5 10 1 1 0 0 1
netname=0V
}
N 72700 39000 72700 36100 4
N 72700 36100 73200 36100 4
N 64300 36100 63800 36100 4
N 63800 36100 63800 39000 4
N 66500 36100 66000 36100 4
N 66000 36100 66000 39000 4
N 68800 36100 68300 36100 4
N 68300 36100 68300 39000 4
N 71000 36100 70500 36100 4
N 70500 36100 70500 39000 4
N 62000 36900 61000 36900 4
N 61000 36900 61000 38700 4
N 61000 38700 63500 38700 4
N 63500 34700 63500 38700 4
N 63500 36500 64300 36500 4
N 64300 36900 63200 36900 4
N 63200 36900 63200 38400 4
N 63200 38400 65700 38400 4
N 65700 35000 65700 38400 4
N 65700 36500 66500 36500 4
N 66500 36900 65400 36900 4
N 65400 36900 65400 38700 4
N 65400 38700 68000 38700 4
N 68000 34700 68000 38700 4
N 68000 36500 68800 36500 4
N 68800 36900 67700 36900 4
N 67700 36900 67700 38400 4
N 67700 38400 70200 38400 4
N 70200 35000 70200 38400 4
N 70200 36500 71000 36500 4
N 71000 36900 69900 36900 4
N 69900 36900 69900 38700 4
N 69900 38700 72400 38700 4
N 72400 34700 72400 38700 4
N 72400 36500 73200 36500 4
N 73200 36900 72000 36900 4
N 72000 36900 72000 38400 4
N 72000 38400 76100 38400 4
N 61000 36500 61000 35000 4
N 61000 35000 64300 35000 4
N 64300 35000 64300 35700 4
N 63500 34700 66500 34700 4
N 66500 34700 66500 35700 4
N 65700 35000 68800 35000 4
N 68800 35000 68800 35700 4
N 68000 34700 71000 34700 4
N 71000 34700 71000 35700 4
N 70200 35000 73200 35000 4
N 73200 35000 73200 35700 4
N 72400 34700 77400 34700 4
C 77400 35300 1 0 0 connector6-2.sym
{
T 77700 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 77700 38350 5 10 0 1 0 0 1
footprint=WS2813
T 78100 38200 5 10 1 1 0 6 1
refdes=PX31
}
C 79700 35300 1 0 0 connector6-2.sym
{
T 80000 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 80000 38350 5 10 0 1 0 0 1
footprint=WS2813
T 80400 38200 5 10 1 1 0 6 1
refdes=PX32
}
C 81900 35300 1 0 0 connector6-2.sym
{
T 82200 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 82200 38350 5 10 0 1 0 0 1
footprint=WS2813
T 82600 38200 5 10 1 1 0 6 1
refdes=PX33
}
C 84200 35300 1 0 0 connector6-2.sym
{
T 84500 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 84500 38350 5 10 0 1 0 0 1
footprint=WS2813
T 84900 38200 5 10 1 1 0 6 1
refdes=PX34
}
C 86400 35300 1 0 0 connector6-2.sym
{
T 86700 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 86700 38350 5 10 0 1 0 0 1
footprint=WS2813
T 87100 38200 5 10 1 1 0 6 1
refdes=PX35
}
C 88600 35300 1 0 0 connector6-2.sym
{
T 88900 38150 5 10 0 0 0 0 1
device=CONNECTOR_6
T 88900 38350 5 10 0 1 0 0 1
footprint=WS2813
T 89300 38200 5 10 1 1 0 6 1
refdes=PX36
}
N 77400 37300 77000 37300 4
N 77000 37300 77000 39900 4
N 88600 37300 88400 37300 4
N 88400 37300 88400 39300 4
N 88400 39300 77000 39300 4
{
T 88300 39300 5 10 1 1 0 0 1
netname=5V0
}
N 79700 37300 79500 37300 4
N 79500 37300 79500 39300 4
N 81900 37300 81700 37300 4
N 81700 37300 81700 39300 4
N 84200 37300 84000 37300 4
N 84000 37300 84000 39300 4
N 86400 37300 86200 37300 4
N 86200 37300 86200 39300 4
N 77400 36100 76700 36100 4
N 76700 36100 76700 39000 4
N 75900 39000 88100 39000 4
{
T 76700 39000 5 10 1 1 0 0 1
netname=0V
}
N 88100 39000 88100 36100 4
N 88100 36100 88600 36100 4
N 79700 36100 79200 36100 4
N 79200 36100 79200 39000 4
N 81900 36100 81400 36100 4
N 81400 36100 81400 39000 4
N 84200 36100 83700 36100 4
N 83700 36100 83700 39000 4
N 86400 36100 85900 36100 4
N 85900 36100 85900 39000 4
N 77400 36900 76400 36900 4
N 76400 36900 76400 38700 4
N 76400 38700 78900 38700 4
N 78900 34700 78900 38700 4
N 78900 36500 79700 36500 4
N 79700 36900 78600 36900 4
N 78600 36900 78600 38400 4
N 78600 38400 81100 38400 4
N 81100 35000 81100 38400 4
N 81100 36500 81900 36500 4
N 81900 36900 80800 36900 4
N 80800 36900 80800 38700 4
N 80800 38700 83400 38700 4
N 83400 34700 83400 38700 4
N 83400 36500 84200 36500 4
N 84200 36900 83100 36900 4
N 83100 36900 83100 38400 4
N 83100 38400 85600 38400 4
N 85600 35000 85600 38400 4
N 85600 36500 86400 36500 4
N 86400 36900 85300 36900 4
N 85300 36900 85300 38700 4
N 85300 38700 87800 38700 4
N 87800 36500 87800 38700 4
N 87800 36500 88600 36500 4
N 76400 36500 76400 35000 4
N 76400 35000 79700 35000 4
N 79700 35000 79700 35700 4
N 78900 34700 81900 34700 4
N 81900 34700 81900 35700 4
N 81100 35000 84200 35000 4
N 84200 35000 84200 35700 4
N 83400 34700 86400 34700 4
N 86400 34700 86400 35700 4
N 85600 35000 88600 35000 4
N 88600 35000 88600 35700 4
N 77400 34700 77400 35700 4
N 76100 38400 76100 36500 4
N 76100 36500 77400 36500 4
N 87800 47200 59000 47200 4
N 59000 47200 59000 42100 4
N 59000 42100 62000 42100 4
N 87800 40800 59000 40800 4
N 59000 40800 59000 35700 4
N 59000 35700 62000 35700 4
N 89900 51200 89900 46800 4
N 89900 46800 59400 46800 4
N 59400 46800 59400 42900 4
N 89900 44800 89900 40400 4
N 89900 40400 59400 40400 4
N 59400 40400 59400 36500 4
C 59700 52800 1 270 0 capacitor-2.sym
{
T 60400 52600 5 10 0 0 270 0 1
device=POLARIZED_CAPACITOR
T 60200 52600 5 10 1 1 270 0 1
refdes=C4
T 60600 52600 5 10 0 0 270 0 1
symversion=0.1
T 59700 52800 5 10 1 1 0 0 1
value=47u
T 59700 52800 5 10 0 0 0 0 1
footprint=1206
}
C 75500 52700 1 270 0 capacitor-2.sym
{
T 76200 52500 5 10 0 0 270 0 1
device=POLARIZED_CAPACITOR
T 76000 52500 5 10 1 1 270 0 1
refdes=C5
T 76400 52500 5 10 0 0 270 0 1
symversion=0.1
T 75500 52700 5 10 1 1 0 0 1
value=47u
T 75500 52700 5 10 0 0 0 0 1
footprint=1206
}
C 60300 46300 1 270 0 capacitor-2.sym
{
T 61000 46100 5 10 0 0 270 0 1
device=POLARIZED_CAPACITOR
T 60800 46100 5 10 1 1 270 0 1
refdes=C6
T 61200 46100 5 10 0 0 270 0 1
symversion=0.1
T 60300 46300 5 10 1 1 0 0 1
value=47u
T 60300 46300 5 10 0 0 0 0 1
footprint=1206
}
C 75800 46300 1 270 0 capacitor-2.sym
{
T 76500 46100 5 10 0 0 270 0 1
device=POLARIZED_CAPACITOR
T 76300 46100 5 10 1 1 270 0 1
refdes=C7
T 76700 46100 5 10 0 0 270 0 1
symversion=0.1
T 75800 46300 5 10 1 1 0 0 1
value=47u
T 75800 46300 5 10 0 0 0 0 1
footprint=1206
}
C 60200 40000 1 270 0 capacitor-2.sym
{
T 60900 39800 5 10 0 0 270 0 1
device=POLARIZED_CAPACITOR
T 60700 39800 5 10 1 1 270 0 1
refdes=C8
T 61100 39800 5 10 0 0 270 0 1
symversion=0.1
T 60200 40000 5 10 1 1 0 0 1
value=47u
T 60200 40000 5 10 0 0 0 0 1
footprint=1206
}
C 75700 39900 1 270 0 capacitor-2.sym
{
T 76400 39700 5 10 0 0 270 0 1
device=POLARIZED_CAPACITOR
T 76200 39700 5 10 1 1 270 0 1
refdes=C9
T 76600 39700 5 10 0 0 270 0 1
symversion=0.1
T 75700 39900 5 10 1 1 0 0 1
value=47u
T 75700 39900 5 10 0 0 0 0 1
footprint=1206
}
N 59900 51900 59900 51800 4
N 59900 52800 61600 52800 4
N 75700 52700 77000 52700 4
N 76000 46300 77000 46300 4
N 60500 46300 61600 46300 4
N 60400 39100 60400 39000 4
N 60400 40000 61600 40000 4
N 75900 39900 77000 39900 4
