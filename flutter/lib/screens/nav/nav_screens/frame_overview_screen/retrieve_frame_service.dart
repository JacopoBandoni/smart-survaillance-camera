import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_smartcam/models/frame.dart';
import 'package:http/http.dart';

class FrameRetriever {
  String url;
  String videoSource;

  FrameRetriever({@required this.url, @required this.videoSource});

  Future<List<Frame>> loadFrame() async {
    List<Frame> listFrame = [];

    Response response1 =
        await get(Uri.parse(url + "?source=" + videoSource + "&metadata=true"));

    print(url + "?source=" + videoSource + "&metadata=true");
    print(response1.body.toString());

    if (response1.statusCode == 200) {
      List<dynamic> body = jsonDecode(response1.body);
      for (Map<String, dynamic> metadata in body) {
        String timestamp = metadata["frame_timestamp"];

        //timestamp =
        //    timestamp.substring(0, 10) + ' ' + timestamp.substring(11, 23);

        listFrame.add(Frame(
            imageUrl: url + "/" + metadata["id"].toString(),
            timestamp: DateTime.parse(timestamp)));
      }
    }

    return listFrame;
  }
}
