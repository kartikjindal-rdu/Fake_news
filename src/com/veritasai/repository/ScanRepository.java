package com.veritasai.repository;

import com.veritasai.model.ScanRecord;

import java.io.File;
import java.io.IOException;
import java.util.List;

/**
 * Data Access Object (DAO) interface for persisting and querying scan records.
 */
public interface ScanRepository {

    void save(ScanRecord record);

    List<ScanRecord> getAll();

    ScanRecord getById(String scanId);

    boolean delete(String scanId);

    void clearAll();

    List<ScanRecord> search(String query, String predictionFilter);

    void exportToCsv(File targetFile) throws IOException;
}
