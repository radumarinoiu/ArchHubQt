import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    property string label: ""
    property int value: 0
    Layout.fillWidth: true
    Layout.minimumWidth: 80
    implicitHeight: 36
    border.color: palette.mid
    border.width: 1
    radius: 4
    color: palette.base

    Text {
        anchors.centerIn: parent
        text: label + ": " + value
        font.pixelSize: 12
    }
}
