import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_smartcam/models/frame.dart';
import 'package:flutter_smartcam/screens/nav/nav_screens/frame_overview_screen/retrieve_frame_service.dart';
import 'package:flutter_smartcam/screens/nav/nav_screens/widgets/refresh_widget.dart';
import 'package:flutter_smartcam/services/server_service.dart';

class FrameOverviewScreen extends StatefulWidget {
  FrameOverviewScreen({Key key}) : super(key: key);

  @override
  _FrameOverviewScreenState createState() => _FrameOverviewScreenState();
}

class _FrameOverviewScreenState extends State<FrameOverviewScreen> {
  List<Frame> listFrame = [];

  FrameRetriever frameRetriever;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) => buildList();

  Widget buildList() => RefreshIndicator(
        onRefresh: () async {
          ServerService serverService =
              RepositoryProvider.of<ServerService>(context);
          frameRetriever = FrameRetriever(
              url: serverService.serverUrl,
              videoSource: serverService.videoSource);
          listFrame = await frameRetriever.loadFrame();
          setState(() {});
        },
        child: listFrame.isEmpty
            ? ListView(children: [
                Padding(
                  padding: const EdgeInsets.all(60.0),
                  child: Center(child: Text("Pull to refresh")),
                )
              ])
            : GridView.builder(
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 5,
                ),
                physics: const BouncingScrollPhysics(
                    parent: AlwaysScrollableScrollPhysics()),
                shrinkWrap: true,
                primary: false,
                itemCount: listFrame.length,
                itemBuilder: (context, index) {
                  final number = listFrame[index];
                  return buildItem(number);
                },
              ),
      );

  Widget buildItem(Frame frame) => InkWell(
      onTap: () => {
            Navigator.push(context, PageRouteBuilder(pageBuilder: (_, __, ___) {
              return ImageViewScreen(
                url: frame.imageUrl,
                timestamp: frame.timestamp,
              );
            }))
          },
      child: Hero(
          tag: frame.imageUrl,
          child: Image.network(
            frame.imageUrl,
          )));
}

class ImageViewScreen extends StatelessWidget {
  final String url;
  final DateTime timestamp;

  const ImageViewScreen({Key key, this.url, this.timestamp}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: Padding(
        padding: const EdgeInsets.all(40.0),
        child: Column(
          children: [
            Hero(tag: url, child: Image.network(url)),
            SizedBox(
              height: 50,
            ),
            Text(formatDateTime(timestamp))
          ],
        ),
      ),
    );
  }

  String formatDateTime(datetime) {
    print(datetime.toString());

    return datetime.month.toString() +
        "/" +
        datetime.day.toString() +
        " " +
        datetime.hour.toString() +
        ":" +
        datetime.minute.toString();
  }
}
