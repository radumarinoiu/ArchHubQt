import QtQuick
import QtQuick.Controls

Rectangle {
    property string pkgName: ""
    property string pkgVersion: ""
    property string pkgSource: ""
    width: ListView.view ? ListView.view.width - 4 : 200
    height: 36
    border.color: selected ? palette.highlight : "transparent"
    border.width: selected ? 2 : 0
    color: selected ? palette.highlight : (mouse.containsMouse ? palette.mid : palette.base)
    radius: 2

    property bool selected: appModel && appModel.selectedPackageName === pkgName

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        onClicked: {
            if (appModel)
                appModel.selectedPackageName = pkgName
        }
    }

    Row {
        anchors.fill: parent
        anchors.margins: 6
        spacing: 8
        Text {
            text: pkgName
            font.pixelSize: 13
            elide: Text.ElideRight
            width: parent.width - versionWidth - 20
        }
        Text {
            id: ver
            text: pkgVersion
            font.pixelSize: 11
            color: palette.mid
        }
        Item { width: 1; height: 1 }
    }

    property real versionWidth: ver.implicitWidth
}
