import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:share_plus/share_plus.dart';
import 'package:http/http.dart';


class ShareImageWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        ElevatedButton(
          onPressed: () => _selectAndShareImage(context),
          child: Text('Select and Share Image'),
        ),
      ],
    );
  }

  Future<void> _selectAndShareImage(BuildContext context) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    final Uri imageURL = "https://localhost:5000/docs";
    
    if (pickedFile != null) {
      final imagePath = pickedFile.path;
      try {
        await Share.shareXFiles([XFile(imagePath)], text: 'Shared Image');
        await post(imageURL);

      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to share image')),
        );
      }
    }
  }
}

void main() {
  runApp(MaterialApp(
    home: Scaffold(
      appBar: AppBar(
        title: Text('Image Sharing'),
      ),
      body: ShareImageWidget(),
    ),
  ));
}
