import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components" as Comp

Pane {
    id: root
    property bool showSearchBar: false

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        RowLayout {
            Layout.fillWidth: true
            Layout.margins: 8
            visible: showSearchBar
            TextField {
                id: searchField
                placeholderText: qsTr("Search packages...")
                Layout.fillWidth: true
                onTextChanged: if (appModel) appModel.searchQuery = text
                onVisibleChanged: if (visible) forceActiveFocus()
            }
            Button {
                text: qsTr("Clear")
                onClicked: { searchField.text = ""; if (appModel) appModel.searchQuery = "" }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            ScrollView {
                id: packageScrollView
                Layout.minimumWidth: 280
                Layout.fillWidth: true
                Layout.fillHeight: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                contentWidth: width
                ListView {
                    id: packageList
                    width: packageScrollView.width > 0 ? packageScrollView.width : root.width - 320
                    clip: true
                    model: packageModel
                    delegate: Comp.PackageDelegate {
                        pkgName: model.name
                        pkgVersion: model.version
                        pkgSource: model.source
                    }
                    onCountChanged: if (appModel) appModel.refreshCounts()
                }
            }

            Comp.PackageDetailsPane {
                Layout.minimumWidth: 320
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        BusyIndicator {
            Layout.alignment: Qt.AlignHCenter
            running: appModel && appModel.loading
            visible: running
        }
        Label {
            Layout.fillWidth: true
            text: appModel ? appModel.errorMessage : ""
            visible: text.length > 0
            color: "red"
            wrapMode: Text.WordWrap
        }
    }

    Component.onCompleted: {
        if (appModel) {
            appModel.packageFilter = appModel.packageFilter
            appModel.refreshPackageList()
        }
    }
}
