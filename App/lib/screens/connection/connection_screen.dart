import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_smartcam/screens/nav/nav_screen.dart';
import 'package:flutter_smartcam/services/server_service.dart';
import 'package:http/http.dart';

class ConnectionScreen extends StatefulWidget {
  static const String routeName = "/conn";

  static Route route() {
    return PageRouteBuilder(pageBuilder: (_, __, ___) {
      return ConnectionScreen();
    });
  }

  @override
  _ConnectionScreenState createState() => _ConnectionScreenState();
}

class _ConnectionScreenState extends State<ConnectionScreen> {
  TextEditingController _textEditingController = TextEditingController();

  bool loading = false;

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async => false,
      child: Scaffold(
        appBar: AppBar(
          title: Text("Connection"),
          leading: Container(),
        ),
        body: Container(
          padding: EdgeInsets.all(20),
          child: loading
              ? Center(child: CircularProgressIndicator())
              : Column(
                  children: [
                    SizedBox(
                      height: 40,
                    ),
                    Text(
                      "Connect to the camera",
                      style: TextStyle(fontSize: 20),
                    ),
                    SizedBox(
                      height: 40,
                    ),
                    TextField(
                      controller: _textEditingController,
                      decoration:
                          InputDecoration(hintText: "http://ipAddress:port"),
                    ),
                  ],
                ),
        ),
        floatingActionButton: FloatingActionButton(
          child: Icon(Icons.control_point),
          onPressed: () async {
            setState(() {
              loading = true;
            });
            try {
              Response response = await get(
                  Uri.parse(_textEditingController.text + "/controller"));

              if (response.statusCode == 200) {
                Map<String, dynamic> body = jsonDecode(response.body);
                RepositoryProvider.of<ServerService>(context).setUrl(
                    serverUrl: body["server_url"],
                    cameraUrl: _textEditingController.text,
                    videoSource: body["camera"]);
                Navigator.pushNamed(context, NavScreen.routeName);
              } else {
                final snackBar = SnackBar(
                  content: Text('Connesione non andata a buon fine'),
                  action: SnackBarAction(
                    label: 'ok',
                    onPressed: () {},
                  ),
                );
                ScaffoldMessenger.of(context).showSnackBar(snackBar);
              }
            } catch (e) {
              final snackBar = SnackBar(
                content: Text('Connesione non andata a buon fine'),
                action: SnackBarAction(
                  label: 'ok',
                  onPressed: () {},
                ),
              );
              ScaffoldMessenger.of(context).showSnackBar(snackBar);
              print(e);
            }

            await Future.delayed(Duration(milliseconds: 100));
            setState(() {
              loading = false;
            });
          },
        ),
      ),
    );
  }
}
