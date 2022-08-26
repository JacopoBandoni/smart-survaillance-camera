import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_datetime_picker/flutter_datetime_picker.dart';
import 'package:flutter_smartcam/screens/nav/nav_screens/streaming_screen/mjpeg.dart';
import 'package:flutter_smartcam/services/server_service.dart';

class StreamingScreen extends StatefulWidget {
  StreamingScreen({Key key}) : super(key: key);

  @override
  _StreamingScreenState createState() => _StreamingScreenState();
}

class _StreamingScreenState extends State<StreamingScreen> {
  DateTime initialDateTime;
  DateTime finalDateTime;

  bool request = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(20),
      child: Center(
        child: Column(
          children: [
            SizedBox(
              height: 30,
            ),
            request
                ? MjpegView(
                    url: RepositoryProvider.of<ServerService>(context)
                            .cameraUrl +
                        "/video?" +
                        "begin=" +
                        adjustDateToServer(initialDateTime) +
                        "&end=" +
                        adjustDateToServer(finalDateTime),
                  )
                : Text("Select interval and request the video"),
            SizedBox(
              height: 30,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                    onPressed: () {
                      DatePicker.showDateTimePicker(context,
                          showTitleActions: true,
                          minTime: DateTime(2021, 3, 5),
                          maxTime: DateTime(2021, 6, 7), onChanged: (date) {
                        print('change $date');
                      }, onConfirm: (date) {
                        setState(() {
                          initialDateTime = date;
                        });
                        print('confirm $date');
                      }, currentTime: DateTime.now(), locale: LocaleType.en);
                    },
                    child: Text("Initial Date Time")),
                ElevatedButton(
                    onPressed: () {
                      DatePicker.showDateTimePicker(context,
                          showTitleActions: true,
                          minTime: DateTime(2021, 3, 5, 0),
                          maxTime: DateTime(2021, 6, 7, 0), onChanged: (date) {
                        print('change $date');
                      }, onConfirm: (date) {
                        setState(() {
                          finalDateTime = date;
                        });
                        print('confirm $date');
                      }, currentTime: DateTime.now(), locale: LocaleType.en);
                    },
                    child: Text("Final Date Time"))
              ],
            ),
            SizedBox(
              height: 10,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                initialDateTime == null
                    ? Text("Inserisci data iniziale")
                    : Text(initialDateTime.month.toString() +
                        "/" +
                        initialDateTime.day.toString() +
                        " " +
                        initialDateTime.hour.toString() +
                        ":" +
                        initialDateTime.minute.toString()),
                finalDateTime == null
                    ? Text("Inserisci data finale")
                    : Text(finalDateTime.month.toString() +
                        "/" +
                        finalDateTime.day.toString() +
                        " " +
                        finalDateTime.hour.toString() +
                        ":" +
                        finalDateTime.minute.toString())
              ],
            ),
            SizedBox(
              height: 40,
            ),
            ElevatedButton(
                onPressed: () {
                  setState(() {
                    request = true;
                  });
                },
                child: Text("Request video"))
          ],
        ),
      ),
    );
  }

  String adjustDateToServer(DateTime dateTime) {
    String dateTimeAdjusted = dateTime.toString();
    dateTimeAdjusted = dateTimeAdjusted.substring(0, 10) +
        " " +
        dateTimeAdjusted.substring(11) +
        "000";
    print(dateTimeAdjusted);

    return dateTimeAdjusted;
  }
}
