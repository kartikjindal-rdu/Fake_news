module AI_Fake_mews_detection {
    requires java.desktop;
    requires java.sql;
    requires java.net.http;

    exports com.fakenews.detector;
    exports com.fakenews.detector.api;
    exports com.fakenews.detector.classifier;
    exports com.fakenews.detector.data;
    exports com.fakenews.detector.gui;
    exports com.fakenews.detector.gui.components;
    exports com.fakenews.detector.model;
    exports com.fakenews.detector.nlp;
}